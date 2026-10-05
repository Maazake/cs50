import sys
import psycopg2
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

        connection = psycopg2.connect("dbname=nbp_tracker user=mazake")
        save_to_postgres(connection, record)
        connection.close()
        
    except requests.RequestException:
        sys.exit("Network error.")

    except psycopg2.Error:
        sys.exit("Database error.")

    except ValueError:
        sys.exit("Not valid currency.")

    print(record)


def validate_symbol(currency: str) -> str:
    currency = currency.strip().upper()

    if currency not in VALID_CURRENCIES:
        raise ValueError

    return currency


def parse_rate(data: dict) -> dict:
    code = data["code"]
    rate = data["rates"][0]["mid"]
    date = data["rates"][0]["effectiveDate"]

    return {"code": code, "rate": rate, "date": date}

def save_to_postgres(connection, record: dict) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO rates (code, rate, date) VALUES (%s, %s, %s)",
            (record["code"], record["rate"], record["date"])
        )
    connection.commit()


def fetch_data(symbol: str) -> dict:
    response = requests.get(
        f"https://api.nbp.pl/api/exchangerates/rates/a/{symbol}/?format=json", timeout=5
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    main()
