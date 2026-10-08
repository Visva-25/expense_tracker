"""data_manager.py - Stores and manages expense records.

Expenses are kept in a Python list of dictionaries, for example:
    {"id": 1, "date": "2026-10-08", "category": "Food",
     "description": "Lunch", "amount": 120.0}

The list is saved to a CSV file (expenses.csv) and the monthly budget is
saved to a JSON file (budget.json), so data is kept after closing the app.
"""

import csv
import json
import os

from validators import (validate_amount, validate_category, validate_date,
                        validate_description, validate_month)

# Files are stored in the "data" folder next to this script.
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
EXPENSE_FILE = os.path.join(DATA_FOLDER, "expenses.csv")
BUDGET_FILE = os.path.join(DATA_FOLDER, "budget.json")

FIELDS = ["id", "date", "category", "description", "amount"]


class DataFileError(Exception):
    """Raised when a data file cannot be read or written."""


# ---------------------------------------------------------------
# File handling (load / save)
# ---------------------------------------------------------------
def load_expenses(path=EXPENSE_FILE):
    """Read all expenses from the CSV file. Returns an empty list if no file."""
    expenses = []
    try:
        with open(path, newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                row["id"] = int(row["id"])
                row["amount"] = float(row["amount"])
                expenses.append(row)
    except FileNotFoundError:
        return []                       # first run: nothing saved yet
    except (ValueError, KeyError) as error:
        raise DataFileError(f"The expense file is damaged: {error}")
    except OSError as error:
        raise DataFileError(f"Could not read the expense file: {error}")
    return expenses


def save_expenses(expenses, path=EXPENSE_FILE):
    """Write all expenses to the CSV file."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(expenses)
    except OSError as error:
        raise DataFileError(f"Could not save the expense file: {error}")


def load_budget(path=BUDGET_FILE):
    """Read the monthly budget. Returns 0 if no budget has been set."""
    try:
        with open(path, encoding="utf-8") as file:
            return float(json.load(file)["monthly_budget"])
    except FileNotFoundError:
        return 0.0
    except (ValueError, KeyError, TypeError):
        raise DataFileError("The budget file is damaged.")
    except OSError as error:
        raise DataFileError(f"Could not read the budget file: {error}")


def save_budget(budget, path=BUDGET_FILE):
    """Save the monthly budget to the JSON file."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump({"monthly_budget": budget}, file)
    except OSError as error:
        raise DataFileError(f"Could not save the budget file: {error}")


# ---------------------------------------------------------------
# Add / Update / Delete
# ---------------------------------------------------------------
def next_id(expenses):
    """Return an unused id (one more than the biggest existing id)."""
    if len(expenses) == 0:
        return 1
    return max(item["id"] for item in expenses) + 1


def find_expense(expenses, expense_id):
    """Return the expense with the given id. Raises ValueError if missing."""
    for item in expenses:
        if item["id"] == expense_id:
            return item
    raise ValueError(f"No expense found with id {expense_id}.")


def add_expense(expenses, date, category, description, amount):
    """Validate the inputs and add a new expense to the list."""
    new_item = {
        "id": next_id(expenses),
        "date": validate_date(date),
        "category": validate_category(category),
        "description": validate_description(description),
        "amount": validate_amount(amount),
    }
    expenses.append(new_item)
    return new_item


def update_expense(expenses, expense_id, date, category, description, amount):
    """Validate the inputs and replace the values of an existing expense."""
    item = find_expense(expenses, expense_id)
    item["date"] = validate_date(date)
    item["category"] = validate_category(category)
    item["description"] = validate_description(description)
    item["amount"] = validate_amount(amount)
    return item


def delete_expense(expenses, expense_id):
    """Remove the expense with the given id from the list."""
    item = find_expense(expenses, expense_id)
    expenses.remove(item)


# ---------------------------------------------------------------
# Search / Filter
# ---------------------------------------------------------------
def search_expenses(expenses, keyword):
    """Return expenses whose description or category contains the keyword."""
    keyword = keyword.strip().lower()
    if keyword == "":
        return list(expenses)
    return [item for item in expenses
            if keyword in item["description"].lower()
            or keyword in item["category"].lower()]


def filter_expenses(expenses, category=None, month=None):
    """Return expenses matching a category and/or a month (YYYY-MM)."""
    result = list(expenses)
    if category:
        result = [item for item in result
                  if item["category"].lower() == category.strip().lower()]
    if month:
        month = validate_month(month)
        result = [item for item in result if item["date"].startswith(month)]
    return result


def get_categories(expenses):
    """Return a sorted list of the categories used so far."""
    return sorted(set(item["category"] for item in expenses))
