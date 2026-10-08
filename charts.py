"""charts.py - Matplotlib charts.

Each function returns a Matplotlib Figure. The GUI shows the figure in a
window, and the figure can also be saved as a PNG image.
"""

from matplotlib.figure import Figure

from analysis import category_summary, monthly_summary


def _empty_chart(title):
    """A placeholder chart used when there is no data."""
    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    ax.text(0.5, 0.5, "No data to show", ha="center", va="center")
    ax.set_title(title)
    ax.axis("off")
    return fig


def category_pie_chart(expenses):
    """Chart 1: pie chart showing how spending is split between categories."""
    title = "Spending by Category"
    summary = category_summary(expenses)
    if summary.empty:
        return _empty_chart(title)

    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    ax.pie(summary["total"], labels=summary["category"], autopct="%1.1f%%")
    ax.set_title(title)
    return fig


def monthly_budget_chart(expenses, budget):
    """Chart 2: bar chart of monthly spending with the budget as a red line."""
    title = "Monthly Spending vs Budget"
    summary = monthly_summary(expenses, budget)
    if summary.empty:
        return _empty_chart(title)

    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)
    ax.bar(summary["month"], summary["spent"], color="steelblue", label="Spent")
    if budget > 0:
        ax.axhline(budget, color="red", linestyle="--", label="Budget")
    ax.set_title(title)
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount")
    ax.legend()
    return fig
