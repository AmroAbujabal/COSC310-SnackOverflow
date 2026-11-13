import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"

DEVELOPMENT_JWT_SECRET = (
    "snackoverflow-local-development-secret-2026"
)


@dataclass(frozen=True)
class Settings:
    data_dir: Path

    jwt_secret: str = field(
        default_factory=lambda: os.getenv(
            "SNACKOVERFLOW_JWT_SECRET",
            DEVELOPMENT_JWT_SECRET,
        )
    )
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

    return Settings(
        data_dir=Path(data_dir) if data_dir else DEFAULT_DATA_DIR,
    )
