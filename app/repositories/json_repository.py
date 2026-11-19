import json
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class JsonRepository(Generic[ModelT]):
    """Shared JSON-file persistence for Pydantic model records."""

    def __init__(self, path: Path, model_type: type[ModelT]):
        self._path = path
        self._model_type = model_type

    def _load(self) -> list[ModelT]:
        with self._path.open(encoding="utf-8") as file:
            rows = json.load(file)
        return [self._model_type(**row) for row in rows]

    def list_all(self) -> list[ModelT]:
        """Return every stored record."""
        return self._load()

    def _save(self, records: list[ModelT]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps([record.model_dump() for record in records], indent=2)
            + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _next_id(existing_ids: list[int]) -> int:
        return max(existing_ids, default=0) + 1
