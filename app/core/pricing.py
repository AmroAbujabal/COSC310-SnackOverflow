from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def _cents(value) -> Decimal:
    # str() first: Decimal(0.1) would keep the float error.
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def money(value: float) -> float:
    """Round to cents, half-up."""
    return float(_cents(value))


def line_total(unit_price: float, quantity: int) -> float:
    return float(_cents(_cents(unit_price) * quantity))


def order_total(line_totals: list[float]) -> float:
    return float(sum((_cents(t) for t in line_totals), Decimal("0")))
