import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: list[int]
    FORMAT_LOGS: str = '{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}'
    LOG_ROTATION: str = '10 MB'

    DB_USER: str
    DB_NAME: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str

    BOT_TOKEN: str

    STORE_URL: str = 'sqlite:///data/jobs.sqlite'
    BASE_SITE: str
    TG_APP_SITE: str
    FRONT_SITE: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))
    
    def get_webhook_url(self):
        return f'{self.BASE_SITE}/webhook'
    
    def get_tg_api_url(self) -> str:
        return f'{self.TG_APP_SITE}/bot{self.BOT_TOKEN}'
    
    @property
    def get_db_url(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


settings = Settings()

database_url = settings.get_db_url
bot_token = settings.BOT_TOKEN

scheduler = AsyncIOScheduler(
    jostore={'default': SQLAlchemyJobStore(url=settings.STORE_URL)})