import pytz
from langchain_community.embeddings import OllamaEmbeddings

from src.docchat_service.base import Singleton
from src.docchat_service.config import APP_CONFIG, Secrets
from src.docchat_service.logger import ContextVarsContainer, LoggerConfigurator

class AppContext(metaclass=Singleton):
    @property
    def logger(self):
        return self._logger_manager.async_logger

    def __init__(self, secrets: Secrets):
        self.timezone = pytz.timezone(secrets.app.timezone)
        self.context_vars_container = ContextVarsContainer()
        self._logger_manager = LoggerConfigurator(
            log_lvl=secrets.log.log_lvl,
            context_vars_container=self.context_vars_container
        )
        self.logger.info("App context initialized for local RAG development")

    def get_logger(self):
        return self.logger

    def get_context_vars_container(self):
        return self.context_vars_container

    def get_pytz_timezone(self):
        return self.timezone

    async def on_startup(self):
        self.logger.info("Application is starting up in local mode")
        self.logger.info("Ready for RAG document processing with Ollama")

    async def on_shutdown(self):
        self.logger.info("Application is shutting down")
        self._logger_manager.remove_logger_handlers()

APP_CTX = AppContext(APP_CONFIG)

__all__ = ["APP_CTX"]