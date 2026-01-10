import os
import json
import zipfile
import tarfile
import re
from pathlib import Path
import chardet

# Типы файлов
TEXT_EXTENSIONS = {'.txt', '.rtf'}
DOC_EXTENSIONS = {'.doc', '.docx'}
PDF_EXTENSIONS = {'.pdf'}
ARCHIVE_EXTENSIONS = {'.zip', '.tar', '.tar.gz', '.gz', '.rar', '.7z'}

try:
    import docx
except ImportError:
    docx = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import rarfile
except ImportError:
    rarfile = None

try:
    import py7zr
except ImportError:
    py7zr = None


class DocumentReader:
    def __init__(self, output_dir="output_jsons"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def read_file(self, file_path: str):
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext in TEXT_EXTENSIONS:
            return self._read_text_file(path)
        elif ext in DOC_EXTENSIONS:
            return self._read_doc_file(path)
        elif ext in PDF_EXTENSIONS:
            return self._read_pdf_file(path)
        elif ext in ARCHIVE_EXTENSIONS:
            return self._read_archive(path)
        else:
            return f"Формат {ext} не поддерживается."

    def _read_text_file(self, path: Path):
        with open(path, 'rb') as f:
            raw_data = f.read()
            encoding = chardet.detect(raw_data)['encoding']
        with open(path, 'r', encoding=encoding) as f:
            return f.read()

    def _read_doc_file(self, path: Path):
        if path.suffix.lower() == '.docx':
            if not docx:
                return "Для .docx установите python-docx."
            doc = docx.Document(str(path))
            full_text = [p.text for p in doc.paragraphs]
            return '\n'.join(full_text)
        elif path.suffix.lower() == '.doc':
            try:
                import win32com.client
                word = win32com.client.Dispatch("Word.Application")
                doc = word.Documents.Open(str(path.resolve()))  # используем .resolve()
                text = doc.Range().Text
                doc.Close()
                word.Quit()
                return text
            except ImportError:
                return "Для .doc установите pywin32: pip install pywin32"
            except Exception as e:
                return f"Ошибка при чтении .doc: {e}"
        else:
            return f"Чтение .doc требует Win32 COM, не поддерживается в этой версии."

    def _read_pdf_file(self, path: Path):
        if fitz:
            doc = fitz.open(str(path))
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        elif PyPDF2:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        else:
            return "Для .pdf установите pymupdf или PyPDF2."

    def _read_archive(self, path: Path):
        from pathlib import PurePath
        archive_path = str(path)
        extract_dir = f"extracted_{path.stem}"
        os.makedirs(extract_dir, exist_ok=True)

        # Папка для JSON: output_jsons/имя_архива (нормализованное)
        archive_name = self._sanitize_filename(path.stem)
        archive_output_dir = self.output_dir / archive_name
        try:
            archive_output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"❌ Не удалось создать папку {archive_output_dir}: {e}")
            return f"Не удалось создать папку для архива {path.name}"

        if path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                for info in zip_ref.infolist():
                    original_name = info.filename
                    # Извлекаем файл
                    zip_ref.extract(info, extract_dir)
                    extracted_path = os.path.join(extract_dir, info.filename)

                    # Проверяем, является ли это файлом (а не папкой) и с нужным расширением
                    if not info.is_dir():
                        file_ext = Path(original_name).suffix.lower()
                        if file_ext in (TEXT_EXTENSIONS | DOC_EXTENSIONS | PDF_EXTENSIONS | ARCHIVE_EXTENSIONS):
                            decoded_name = self._decode_filename_safe(original_name)
                            rel_path = self._sanitize_filename(decoded_name)
                            json_path = archive_output_dir / rel_path
                            json_path = json_path.with_suffix('.json')  # заменяем расширение на .json
                            json_path.parent.mkdir(parents=True, exist_ok=True)

                            content = self.read_file(extracted_path)
                            self._save_json_with_path(json_path, content)
                        else:
                            print(f"⚠️ Пропущен файл: {original_name} (неподдерживаемое расширение)")

        elif path.suffix in ['.tar', '.tar.gz']:
            mode = 'r:gz' if path.suffix == '.tar.gz' else 'r'
            with tarfile.open(archive_path, mode) as tar_ref:
                for member in tar_ref.getmembers():
                    if member.isfile():
                        file_ext = Path(member.name).suffix.lower()
                        if file_ext in (TEXT_EXTENSIONS | DOC_EXTENSIONS | PDF_EXTENSIONS | ARCHIVE_EXTENSIONS):
                            tar_ref.extract(member, extract_dir)
                            rel_path = self._sanitize_filename(member.name)
                            json_path = archive_output_dir / rel_path
                            json_path = json_path.with_suffix('.json')
                            json_path.parent.mkdir(parents=True, exist_ok=True)
                            extracted_path = os.path.join(extract_dir, member.name)
                            content = self.read_file(extracted_path)
                            self._save_json_with_path(json_path, content)
                        else:
                            print(f"⚠️ Пропущен файл: {member.name} (неподдерживаемое расширение)")

        elif path.suffix == '.rar':
            if not rarfile:
                return "Для .rar установите rarfile."
            with rarfile.RarFile(archive_path) as rar_ref:
                for info in rar_ref.infolist():
                    if info.is_file():
                        file_ext = Path(info.filename).suffix.lower()
                        if file_ext in (TEXT_EXTENSIONS | DOC_EXTENSIONS | PDF_EXTENSIONS | ARCHIVE_EXTENSIONS):
                            rar_ref.extract(info, extract_dir)
                            rel_path = self._sanitize_filename(info.filename)
                            json_path = archive_output_dir / rel_path
                            json_path = json_path.with_suffix('.json')
                            json_path.parent.mkdir(parents=True, exist_ok=True)
                            extracted_path = os.path.join(extract_dir, info.filename)
                            content = self.read_file(extracted_path)
                            self._save_json_with_path(json_path, content)
                        else:
                            print(f"⚠️ Пропущен файл: {info.filename} (неподдерживаемое расширение)")

        elif path.suffix == '.7z':
            if not py7zr:
                return "Для .7z установите py7zr."
            with py7zr.SevenZipFile(archive_path, mode='r') as szf:
                szf.extractall(path=extract_dir)
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file).suffix.lower()
                    if file_ext in (TEXT_EXTENSIONS | DOC_EXTENSIONS | PDF_EXTENSIONS | ARCHIVE_EXTENSIONS):
                        rel_path = os.path.relpath(file_path, extract_dir)
                        safe_rel_path = self._sanitize_filename(rel_path)
                        json_path = archive_output_dir / safe_rel_path
                        json_path = json_path.with_suffix('.json')
                        json_path.parent.mkdir(parents=True, exist_ok=True)
                        content = self.read_file(file_path)
                        self._save_json_with_path(json_path, content)
                    else:
                        print(f"⚠️ Пропущен файл: {file} (неподдерживаемое расширение)")

        else:
            return f"Архив {path.suffix} не поддерживается."

        return f"Файлы из архива {path.name} сохранены в структуре: {archive_output_dir}"

    def _decode_filename_safe(self, filename: str) -> str:
        """
        Пытаемся корректно декодировать имя файла из архива.
        Особенно важно для ZIP, где имена могут быть в CP866.
        """
        try:
            # Проверяем, содержит ли имя кириллицу
            filename.encode('ascii')
            # Если да — возвращаем как есть
            return filename
        except UnicodeEncodeError:
            # Если нет — значит, кириллица, декодируем
            try:
                # ZIP может хранить имена в CP866, но Python читает как CP437
                original_bytes = filename.encode('cp437')
                return original_bytes.decode('cp866', errors='ignore') or filename
            except (UnicodeDecodeError, UnicodeEncodeError):
                return filename

    def _sanitize_filename(self, filename: str) -> str:
        """
        Оставляет кириллицу, латиницу, числа, пробелы, точки, скобки, тире и т.д.
        Удаляет только недопустимые символы для файловой системы.
        """
        # Удаляем недопустимые символы для Windows/Linux/Mac
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Также убираем точки в конце и в начале, если они одиночные
        filename = filename.strip('. ')
        # Убираем лишние пробелы
        filename = re.sub(r'\s+', ' ', filename)
        return filename

    def _save_json_with_path(self, json_path: Path, data):
        try:
            json_path.write_text(
                json.dumps({"filename": json_path.name, "content": data}, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            print(f"✅ Сохранено: {json_path}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении {json_path}: {e}")

    def process_file(self, input_path: str):
        path = Path(input_path)
        content = self.read_file(input_path)

        if path.suffix.lower() in ARCHIVE_EXTENSIONS:
            # Архивы уже сохраняют файлы внутри _read_archive
            return content

        # Для одиночного файла: сохраняем в корень output_jsons
        json_path = self.output_dir / f"{path.stem}.json"
        self._save_json_with_path(json_path, content)
        return f"Файл {input_path} сохранён как JSON: {json_path}"


def main():
    print("Тестирование DocumentReader (поддержка .doc и кириллица в именах файлов из архива)")
    reader = DocumentReader()

    while True:
        file_path = input("\nВведите путь к файлу (или 'quit' для выхода): ").strip()
        if file_path.lower() == 'quit':
            break
        if not os.path.exists(file_path):
            print("Файл не найден.")
            continue

        try:
            result = reader.process_file(file_path)
            print(result)
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()