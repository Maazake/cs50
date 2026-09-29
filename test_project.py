import pytest
import csv
from project import parse_rate, save_to_csv, validate_symbol

test_request = {
    "table": "A",
    "currency": "dolar amerykański",
    "code": "USD",
    "rates": [{"no": "185/A/NBP/2026", "effectiveDate": "2026-09-23", "mid": 3.8175}],
}


def test_validate_symbol():
    assert validate_symbol("usd") == "USD"


def test_validate_symbol_invalid():
    with pytest.raises(ValueError):
        validate_symbol("eru")


def test_parse_rate():
    assert parse_rate(test_request) == {
        "code": "USD",
        "rate": 3.8175,
        "date": "2026-09-23",
    }


def test_parse_rate_missing_rates():
    with pytest.raises(KeyError):
        parse_rate({"code": "USD"})


def test_save_to_csv(tmp_path):
    path = tmp_path / "history.csv"

    first = {
        "code": "USD",
        "rate": 3.8175,
        "date": "2026-09-23",
    }

    second = {
        "code": "EUR",
        "rate": 4.02,
        "date": "2026-09-24",
    }

    save_to_csv(path, first)
    save_to_csv(path, second)

    with open(path) as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 2
    assert rows[0]["code"] == "USD"
    assert rows[1]["code"] == "EUR"

