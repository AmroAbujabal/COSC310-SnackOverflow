
import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class Settings:
    data_dir: Path

    jwt_secret: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    @property
    def restaurants_file(self) -> Path:
        return self.data_dir / "restaurants.json"

    @property
    def menus_file(self) -> Path:
        return self.data_dir / "menus.json"

    @property
    def customers_file(self) -> Path:
        return self.data_dir / "customers.json"


def get_settings() -> Settings:
    data_dir = os.getenv("SNACKOVERFLOW_DATA_DIR")
    jwt_secret = os.getenv(
        "SNACKOVERFLOW_JWT_SECRET",
        "development-only-change-me",
    )

    return Settings(
        data_dir=Path(data_dir) if data_dir else DEFAULT_DATA_DIR,
        jwt_secret=jwt_secret,
    )
