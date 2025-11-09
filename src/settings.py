from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    database_url: str
    max_rooms_managed_by_user: int
    min_players_to_start_game: int = 4
