# NBP Currency Rate History
#### Description:

This is my final project for CS50's Introduction to Programming with Python. It's a small command-line tool that checks the current exchange rate for a currency (like USD or EUR) using the National Bank of Poland (NBP) API, and saves the result to a CSV file so I can build up a little history over time.

I didn't want to build something huge with a UI or a database — the point of this project for me was to actually understand a full, small pipeline: ask for input, check that it's valid, get real data from the internet, turn that messy data into something clean, and save it somewhere. That's basically what a lot of real programs do, just bigger.

## How It Works

You run it like this:

```bash
python project.py
```

It'll ask you to type in a currency code, like `USD`, `EUR`, or `GBP`. I made it case-insensitive and it strips extra spaces, so typing `usd` works the same as `USD`. If you type something that isn't a currency I support, it just tells you and doesn't even try to call the API — no point making a request I already know is wrong.

If the code is valid, the program asks the NBP API for the latest rate, pulls out just the parts I actually need (the code, the rate, and the date), and adds a new line to `history.csv`. The first time it runs, it also writes a header row so the file looks like a proper table. Every time after that, it just appends — so if you run it a few times over a few days, you end up with a little price history.

I also added a 5 second timeout on the network request and check the response status, so if the internet cuts out, or NBP's server is down, or something goes wrong, the program tells me clearly instead of pretending everything went fine and saving garbage data.

## Files

**`project.py`** — this is the whole program. It uses `requests` to talk to the API, `csv` to write the history file, and a couple of built-in modules (`sys`, `pathlib`) for smaller things like exiting cleanly and checking if the CSV file already exists.

Inside `project.py`, I split things into separate functions instead of writing one giant block of code:

- **`main()`** — this is the part that actually talks to the user. It asks for input, calls the other functions in order, and prints out what happened or shows an error if something failed.
- **`validate_symbol(currency)`** — cleans up whatever the user typed (uppercase, no extra spaces) and checks it against the list of currencies I support. If it's not valid, it raises a `ValueError`.
- **`fetch_data(symbol)`** — builds the URL for the NBP API and makes the actual request. This is the only function that touches the network.
- **`parse_rate(data)`** — takes the JSON I got back from the API and pulls out just `code`, `rate`, and `date` into a simple dictionary. If the data is missing something it expects, it just lets the `KeyError` happen instead of hiding the problem.
- **`save_to_csv(path, record)`** — adds one row to the CSV file, writing the header first if the file doesn't exist yet.

**`test_project.py`** — automated tests using pytest. I test the currency validation (valid and invalid codes), the parsing function with fake sample data, what happens when data is missing fields, and writing to the CSV file. Tests use a temporary folder so they never touch my real `history.csv`.

**`requirements.txt`** — just lists `requests`, since that's the only thing I need to install myself. Everything else I used (`csv`, `sys`, `pathlib`) comes built into Python.

**`history.csv`** — this gets created automatically the first time you run the program. It just keeps growing with one row per run.

## Design Decisions

I went with a plain CSV file instead of a database. Mostly because at this point in the course I haven't learned SQL yet, and a CSV is honestly enough for what this project needs — just appending small rows of data. It's also nice that I can open it and read it myself without any extra tools.

The biggest decision I made was splitting the "get data from the internet" part (`fetch_data`) from the "make sense of that data" part (`parse_rate`). At first I had it all in one function, but that made it impossible to test properly — I'd either need internet access every time I ran the tests, or I'd get different results depending on the day's exchange rate. By separating them, I can test `parse_rate` with a fixed, fake API response and know exactly what the result should be, no internet needed.

I also decided to only use the first rate the API gives back, since that's the latest one. I'm not trying to average rates or compare old ones — just checking what the rate is right now.

## Out of Scope

Things this project doesn't do, on purpose: no graphical interface, no login system, no database, no charts, no automatic updates on a schedule, and no converting between two currencies you pick yourself. It also doesn't cache anything for offline use or retry a request if it fails — if the network call fails, it just tells you and stops. And it doesn't clean up or remove duplicate rows from `history.csv` — every successful run just adds another line, even if you check the same currency twice in a row.

## Testing

Run the tests with:

```bash
pytest -q
```

The tests don't make any real network calls — they only test the parts of the program that don't need the internet (validation, parsing, saving to CSV). The one function that actually calls the API, `fetch_data`, isn't automatically tested — I checked that one by hand, running the program with a valid currency, an invalid one, and once with my WiFi turned off to see what happens.