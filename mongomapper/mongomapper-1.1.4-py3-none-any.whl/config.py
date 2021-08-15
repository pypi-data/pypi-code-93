from pydantic import BaseSettings

class Settings(BaseSettings):
  DB_HOST: str = 'localhost'
  DB_PORT: int = 27017
  DB_NAME: str = 'default'
  DB_USER: str
  DB_PASS: str

  class Config:
    env_file = '.env'

config = Settings()