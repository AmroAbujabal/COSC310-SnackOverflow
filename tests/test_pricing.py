from app.services.pricing import line_total, money, order_total


def test_money_avoids_float_error():
    # Plain floats give 0.30000000000000004.
    assert money(0.1 + 0.2) == 0.3


def test_money_rounds_half_up():
    # round(2.675, 2) gives 2.67 in plain Python.
    assert money(2.675) == 2.68


def test_line_total():
    assert line_total(15.99, 3) == 47.97


def test_order_total():
    assert order_total([47.97, 13.99, 0.1]) == 62.06
