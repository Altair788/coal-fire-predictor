from pathlib import Path

from environs import Env
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

env = Env()
env.read_env(ENV_PATH, override=True)


class Settings(BaseModel):
    debug: bool = env.bool("DEBUG", default=False)

    postgres_host: str = env.str("POSTGRES_HOST")
    postgres_port: int = env.int("POSTGRES_PORT")
    postgres_user: str = env.str("POSTGRES_USER")
    postgres_password: str = env.str("POSTGRES_PASSWORD")
    postgres_db: str = env.str("POSTGRES_DB", default="coal_fire_predictor")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
