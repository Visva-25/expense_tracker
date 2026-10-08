"""validators.py - Input validation helpers.

Every function checks one input. If the input is bad, it raises a
ValueError with a friendly message that the GUI shows to the user.
"""

from datetime import datetime


def validate_date(text):
    """Return the date as 'YYYY-MM-DD'. Raises ValueError if invalid."""
    text = text.strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format (e.g. 2026-10-08).")


def validate_amount(text):
    """Return the amount as a float. Must be a number greater than 0."""
    try:
        amount = float(str(text).strip())
    except ValueError:
        raise ValueError("Amount must be a number (e.g. 250 or 99.50).")
    if amount <= 0:
        raise ValueError("Amount must be greater than 0.")
    return round(amount, 2)


def validate_category(text):
    """Return the category in Title Case. Must not be empty."""
    text = text.strip()
    if text == "":
        raise ValueError("Category cannot be empty.")
    return text.title()


def validate_description(text):
    """Return the description (can be empty, but commas are not needed)."""
    return text.strip()


def validate_month(text):
    """Return a month as 'YYYY-MM'. Raises ValueError if invalid."""
    text = text.strip()
    try:
        return datetime.strptime(text, "%Y-%m").strftime("%Y-%m")
    except ValueError:
        raise ValueError("Month must be in YYYY-MM format (e.g. 2026-10).")


def validate_budget(text):
    """Return the monthly budget as a float. Must be greater than 0."""
    try:
        budget = float(str(text).strip())
    except ValueError:
        raise ValueError("Budget must be a number (e.g. 5000).")
    if budget <= 0:
        raise ValueError("Budget must be greater than 0.")
    return round(budget, 2)
