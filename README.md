# Splitzy

A simple expense splitter for friend groups. Add your squad, log receipts, and see who pays who. Built with Python, `decimal` and CustomTkinter.

## Features

- **Exact money math:** every amount uses `decimal.Decimal`, so there are no float rounding errors. Leftover cents are shared out one by one, so splits always add up to the receipt.
- **Fair splits:** pick who paid and who was in on each receipt.
- **Fewest payments:** the app works out a short list of transfers that settles everyone.
- **Group chat ready:** copy the recap in one click.
- **Currencies:** switch between `$`, `€`, `£` and `₹`.
- **Dark mode UI** with rounded cards, emoji and icons.

## Requirements

- Python 3.9 or newer

## Install

```bash
git clone https://github.com/Gyandeep09/expense-splitter.git
cd expense-splitter
python -m venv .venv
```

Activate the environment:

```powershell
# PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Git Bash
source .venv/Scripts/activate
```

Install the dependency:

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

## Test

```bash
pip install -r requirements-dev.txt
pytest
```

## Project layout

| File | Purpose |
| --- | --- |
| `app.py` | CustomTkinter interface |
| `splitter.py` | Money parsing, splitting and settlement logic, no GUI code |
| `tests/` | pytest tests for `splitter.py` |

## How the split works

1. Each receipt is divided by the number of people in it and rounded down to the cent.
2. The leftover cents go to people one at a time, starting from a different person on each receipt so nobody always pays the extra cent.
3. Balances are added up across all receipts. Whoever is owed money gets paid by whoever owes money, largest amounts first.

## License

MIT

