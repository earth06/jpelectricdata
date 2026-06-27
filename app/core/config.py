from pathlib import Path


class Settings:
    """Application settings loaded from local defaults."""

    def __init__(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[2]
        self.db_path = self.repo_root / "data" / "data.db"
        self.power_mbtiles_path = self.repo_root / "data" / "power.mbtiles"
        self.app_name = "JP Electric Dashboard"

    @property
    def database_url(self) -> str:
        """Return a SQLAlchemy URL for the local SQLite database."""
        return f"sqlite:///{self.db_path}"


settings = Settings()
