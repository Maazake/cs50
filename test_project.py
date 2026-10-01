import csv
from unittest.mock import Mock

import pytest
import requests

from project import fetch_data, parse_rate, save_to_csv, validate_symbol

test_request = {
    "table": "A",
    "currency": "dolar amerykański",
    "code": "USD",
    "rates": [{"no": "185/A/NBP/2026", "effectiveDate": "2026-09-23", "mid": 3.8175}],
}


@pytest.mark.parametrize(
    "currency, expected", [("usd", "USD"), ("eur", "EUR"), (" gbp   ", "GBP")]
)
def test_validate_symbol(currency, expected):
    assert validate_symbol(currency) == expected


@pytest.mark.parametrize("bad_currency", ["cat", "123", "US"])
def test_validate_symbol_invalid(bad_currency):
    with pytest.raises(ValueError):
        validate_symbol(bad_currency)


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


def test_fetch_data(monkeypatch):
    fake_response = Mock()

    fake_response.json.return_value = {
        "code": "USD",
        "rates": [
            {"no": "185/A/NBP/2026", "effectiveDate": "2026-09-23", "mid": 3.8175}
        ],
    }

    monkeypatch.setattr("project.requests.get", lambda url, timeout: fake_response)

    result = fetch_data("usd")

    assert result["code"] == "USD"


def test_fetch_data_network_error(monkeypatch):
    def fake_get(url, timeout):
        raise requests.ConnectionError

    monkeypatch.setattr("project.requests.get", fake_get)

    with pytest.raises(requests.RequestException):
        fetch_data("usd")
