from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:123456@localhost:3306/garbage_db"
    secret_key: str = "garbage-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    upload_dir: str = "laji3"
    laji1_dir: str = "laji1"  # 数据集目录，直接读取不复制
    model_dir: str = "ml_models"  # 模型文件目录，存放 .h5 等。train.py 输出可放此目录

    class Config:
        env_file = ".env"


settings = Settings()
