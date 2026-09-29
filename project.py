import csv
import sys
from pathlib import Path

import requests

VALID_CURRENCIES = {
    "USD",
    "EUR",
    "GBP",
    "CHF",
    "JPY",
    "CAD",
    "AUD",
    "NZD",
    "NOK",
    "HKD",
    "SEK",
    "CZK",
    "DKK",
    "HUF",
    "RON",
    "BGN",
    "TRY",
    "UAH",
    "THB",
    "SGD",
}


def main():
    try:
        currency = validate_symbol(input("Currency: "))
        symbol = currency.lower()
        response = fetch_data(symbol)
        record = parse_rate(response)

        path = Path("history.csv")
        save_to_csv(path, record)

    except requests.RequestException:
        sys.exit("Network error.")

    except ValueError:
        sys.exit("Not valid currency.")

    print(record)


def validate_symbol(currency):
    currency = currency.strip().upper()

    if currency not in VALID_CURRENCIES:
        raise ValueError

    return currency


def parse_rate(data):
    code = data["code"]
    rate = data["rates"][0]["mid"]
    date = data["rates"][0]["effectiveDate"]

    return {"code": code, "rate": rate, "date": date}


def save_to_csv(path, record):
    file_exists = path.exists()

    with open(path, "a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["code", "rate", "date"])

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)


def fetch_data(symbol):
    response = requests.get(f"https://api.nbp.pl/api/exchangerates/rates/a/{symbol}/?format=json", timeout=5)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    main()
