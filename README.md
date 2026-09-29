## NBP Currency Rate History

This project is a small command-line currency-rate tracker written in Python. It asks the user for a three-letter currency code, retrieves the latest rate from the National Bank of Poland (NBP) API, converts the API response into a small and predictable record, and appends that record to a local CSV file called `history.csv`. The project was created as a final CS50 Introduction to Programming with Python project and focuses on a complete, understandable data flow rather than a large user interface.

### How It Works

Run the program from the project directory:

```bash
python project.py
```

The program prompts for a currency code such as `USD`, `EUR`, or `GBP`. Input is stripped of surrounding whitespace and converted to uppercase, so `usd` and `USD` are treated the same way. If the code is not in the supported currency set, the program exits with an error message instead of making an invalid request.

For a valid code, the program calls the NBP exchange-rate API. The response is expected to contain a currency code and a `rates` list. The first rate in that list is converted into a simpler record with three fields: `code`, `rate`, and `date`. That record is appended to `history.csv`. The CSV header is written only when the file is created for the first time, so repeated runs add rows without duplicating the header.

The program uses a five-second network timeout and calls `raise_for_status()` on the HTTP response. This means that connection failures, timeouts, and HTTP error responses are handled as network errors instead of being silently treated as valid data.

### Files

`project.py` contains the application itself. It imports `requests` for HTTP requests, `csv` for writing history records, `sys` for clean command-line exits, and `Path` for checking whether the CSV file already exists.

The functions in `project.py` have separate responsibilities:

- `main()` coordinates the application. It reads the user's input, validates it, fetches the API response, parses the response, saves the record, and prints the saved record. It also handles invalid input and network errors at the application boundary.
- `validate_symbol(currency)` normalizes the user's input and checks it against the supported ISO-style currency symbols. It returns the uppercase symbol or raises `ValueError` for an unsupported symbol.
- `fetch_data(symbol)` builds the NBP API URL, makes one HTTP request with a timeout, checks the HTTP status, and returns the decoded JSON dictionary.
- `parse_rate(data)` transforms the nested API response into a simple dictionary. It maps `data["code"]` to `code`, the first rate's `mid` value to `rate`, and its `effectiveDate` value to `date`. Missing required fields are allowed to raise `KeyError`, which makes malformed data visible instead of hiding it.
- `save_to_csv(path, record)` appends one record to the CSV file. It uses `csv.DictWriter`, writes the header when the path did not exist before the write, and then writes the record.

`test_project.py` contains automated tests written with pytest. It tests currency normalization, invalid currency input, API-response parsing, missing `rates` data, and writing two records to a temporary CSV file. The temporary directory fixture keeps tests isolated from the real `history.csv` file. The CSV test also verifies that two records can be written without duplicating the header.

`requirements.txt` lists the external dependency, `requests`, used to communicate with the NBP API. The `csv`, `sys`, and `pathlib` modules come with Python and therefore do not need to be installed separately.

`history.csv` is the local output file created by the application. It is intentionally treated as an append-only history for this small project. It has the columns `code`, `rate`, and `date`.

### Design Decisions

The application uses CSV instead of a database because the project only needs to append small, flat records, and SQL and database administration were outside the scope of the course material at this stage. CSV is easy to inspect manually, easy to back up, and supported by Python's standard library.

The code separates validation, network access, parsing, and persistence. This makes each part easier to understand and test. In particular, `parse_rate` does not perform an HTTP request: it accepts a dictionary, which allows tests to use fixed sample data without depending on the network or on changing exchange rates.

The program uses the first rate returned by the NBP API, because the API response used by this project contains the latest rate in that position. It does not attempt to calculate averages, compare historical rates, or convert between arbitrary currencies.

### Out of Scope

This project does not provide a graphical interface, authentication, a database, charts, automatic scheduled updates, or currency conversion between two user-selected currencies. It does not cache API responses for offline use and does not retry failed network requests. It also does not remove duplicate records from `history.csv`; each successful run represents another observation and is appended as a new row.

### Testing

Run the automated tests with:

```bash
pytest -q
```

The tests do not make real HTTP requests. The network-dependent function is intended to be checked manually by running the program with a valid code, an invalid code, and, when possible, without an internet connection.
