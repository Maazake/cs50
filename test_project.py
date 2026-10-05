from unittest.mock import Mock

import pytest
import requests
import psycopg2

from project import fetch_data, parse_rate, save_to_postgres, validate_symbol

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

import psycopg2

@pytest.fixture
def test_connection():
    conn = psycopg2.connect("dbname=nbp_tracker user=mazake")
    yield conn
    conn.rollback()
    conn.close()


def test_save_to_postgres(test_connection):
    record = {"code": "USD", "rate": 3.8175, "date": "2026-09-23"}
    save_to_postgres(test_connection, record)

    with test_connection.cursor() as cursor:
        cursor.execute("SELECT code FROM rates WHERE code = 'USD'")
        result = cursor.fetchone()

    assert result[0] == "USD"

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
