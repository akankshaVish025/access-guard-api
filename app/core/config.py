import os
from dataclasses import dataclass
from pathlib import Path


def _default_database_url() -> str:
    # Resolve DB path relative to project root, not current shell directory.
    project_root = Path(__file__).resolve().parents[2]
    db_path = project_root / "app.db"
    return f"sqlite:///{db_path.as_posix()}"


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    database_url: str


settings = Settings(
    app_name=os.getenv("APP_NAME", "Auth Access API"),
    app_version=os.getenv("APP_VERSION", "1.0.0"),
    database_url=os.getenv("DATABASE_URL", _default_database_url()),
)
