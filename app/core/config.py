import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"


@dataclass(frozen=True)
class Settings:
    data_dir: Path

    @property
    def restaurants_file(self) -> Path:
        return self.data_dir / "restaurants.json"


def get_settings() -> Settings:
    data_dir = os.getenv("SNACKOVERFLOW_DATA_DIR")
    return Settings(data_dir=Path(data_dir) if data_dir else DEFAULT_DATA_DIR)
