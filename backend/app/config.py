from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Documind API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 文件配置
    UPLOAD_DIR: str = "data/documents"
    MAX_FILE_SIZE: int = 15 * 1024 * 1024  # 15MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".epub"]

    # AI配置
    TONGYI_API_KEY: str = ""
    TONGYI_MODEL: str = "qwen3.6-plus"
    EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"

    # 向量数据库配置
    CHROMA_PERSIST_DIR: str = "data/chroma_db"

    # 记忆配置
    MAX_HISTORY_LENGTH: int = 10
    SUMMARY_LENGTH: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
