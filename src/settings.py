from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    max_rooms_managed_by_user: int
