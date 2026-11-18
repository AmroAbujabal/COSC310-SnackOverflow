import json
from contextlib import contextmanager
from threading import RLock

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.models.cart import Cart

# All instances in one server process share the lock. Run with one worker.
_cart_lock = RLock()


class CartRepository:
    """One retained active cart per customer; clear reuses its stable ID."""

    def __init__(self, settings: Settings):
        self._path = settings.carts_file

    def list_all(self) -> list[Cart]:
        with _cart_lock:
            rows = json.loads(self._path.read_text(encoding="utf-8"))
            carts = [Cart.model_validate(row) for row in rows]
            if len({c.id for c in carts}) != len(carts):
                raise ValueError("Duplicate cart IDs")
            if len({c.customer_id for c in carts}) != len(carts):
                raise ValueError("Duplicate active customer carts")
            return carts

    def get_active(self, customer_id: int) -> Cart | None:
        return next((c for c in self.list_all() if c.customer_id == customer_id), None)

    @contextmanager
    def transaction(self):
        """Validate and save once on success; exceptions leave stored state intact."""
        with _cart_lock:
            carts = self.list_all()
            yield carts
            validated = [Cart.model_validate(c.model_dump()) for c in carts]
            if len({c.id for c in validated}) != len(validated):
                raise ValueError("Duplicate cart IDs")
            if len({c.customer_id for c in validated}) != len(validated):
                raise ValueError("Duplicate active customer carts")
            temporary = self._path.with_suffix(".tmp")
            try:
                temporary.write_text(json.dumps([c.model_dump() for c in validated], indent=2) + "\n", encoding="utf-8")
                temporary.replace(self._path)
            finally:
                temporary.unlink(missing_ok=True)


def get_cart_repository(settings: Settings = Depends(get_settings)) -> CartRepository:
    return CartRepository(settings)
