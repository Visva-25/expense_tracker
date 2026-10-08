"""main.py - Start the Expense Tracker application.

Run with:   python main.py
"""

import tkinter as tk

from gui import ExpenseApp


def main():
    root = tk.Tk()
    ExpenseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
