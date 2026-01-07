import uvicorn

from src.docchat_service.api import app_main
from src.docchat_service.config import APP_CONFIG
from src.docchat_service.logger.uvicorn_logging_config import LOGGING_CONFIG

def main():
    uvicorn.run(
        app_main,
        host=APP_CONFIG.app.app_host,
        port=APP_CONFIG.app.app_port,
        access_log=False,
        log_config=LOGGING_CONFIG,
        reload=APP_CONFIG.log.log_lvl == 10  # Включить reload только в DEBUG
    )

if __name__ == "__main__":
    main()