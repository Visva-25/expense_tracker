"""used to do calculation on the basis of expenses using panda and numpy

All functions take the list of expense dictionaries from data_manager.py
and return numbers or small tables (DataFrames).
"""

import numpy as np
import pandas as pd

from data_manager import FIELDS


def to_dataframe(expenses):
    """Convert the expense list into a Pandas table with a 'month' column."""
    df = pd.DataFrame(expenses, columns=FIELDS)
    df["amount"] = df["amount"].astype(float)
    df["month"] = df["date"].astype(str).str[:7]     # "2026-10-08" -> "2026-10"
    return df


def total_spent(expenses, month=None):
    """Total of all expenses (or only one month if month='YYYY-MM')."""
    df = to_dataframe(expenses)
    if month:
        df = df[df["month"] == month]
    return float(np.sum(df["amount"].to_numpy()))


def category_summary(expenses):
    """Table of total, count and percentage per category (biggest first)."""
    df = to_dataframe(expenses)
    if df.empty:
        return pd.DataFrame(columns=["category", "total", "count", "percent"])
    summary = df.groupby("category")["amount"].agg(["sum", "count"]).reset_index()
    summary.columns = ["category", "total", "count"]
    summary["percent"] = np.round(summary["total"] / summary["total"].sum() * 100, 1)
    return summary.sort_values("total", ascending=False).reset_index(drop=True)


def major_spending_areas(expenses, top_n=3):
    """The top categories where most money is spent."""
    return category_summary(expenses).head(top_n)


def monthly_summary(expenses, budget):
    """Table of spending per month compared with the monthly budget.

    'difference' = budget - spent.
    Negative difference means the budget was exceeded.
    """
    df = to_dataframe(expenses)
    if df.empty:
        return pd.DataFrame(columns=["month", "spent", "budget", "difference", "status"])
    summary = df.groupby("month")["amount"].sum().reset_index()
    summary.columns = ["month", "spent"]
    summary["budget"] = budget
    summary["difference"] = summary["budget"] - summary["spent"]
    if budget > 0:
        summary["status"] = np.where(summary["difference"] < 0,
                                     "Over budget", "Within budget")
    else:
        summary["status"] = "No budget set"
    return summary.sort_values("month").reset_index(drop=True)


def budget_status(expenses, budget, month):
    """Budget usage for one month. Returns a dictionary of results."""
    spent = total_spent(expenses, month)
    remaining = budget - spent
    percent_used = (spent / budget * 100) if budget > 0 else 0.0
    return {
        "month": month,
        "budget": budget,
        "spent": spent,
        "remaining": remaining,
        "percent_used": round(percent_used, 1),
        "over_budget": budget > 0 and spent > budget,
    }
