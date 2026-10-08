"""gui.py - The Tkinter user interface (kept deliberately simple).

Layout (top to bottom):
    1. Form       - date, category, description, amount + Add/Update/Delete/Clear
    2. Filters    - search box, category, month + Apply/Reset
    3. Table      - list of expenses (click a row to edit it)
    4. Bottom bar - set budget, show summary, show the two charts, save chart
"""

import tkinter as tk
from datetime import date
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import analysis
import charts
import data_manager as dm
from validators import validate_budget


class ExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("760x560")

        # Data loaded from files (errors are shown in a message box)
        self.expenses = []
        self.budget = 0.0
        self.selected_id = None
        self.load_data()

        self.build_form()
        self.build_filters()
        self.build_table()
        self.build_bottom_bar()
        self.refresh_table()

    # ----------------------------------------------------------
    # Loading and saving
    # ----------------------------------------------------------
    def load_data(self):
        try:
            self.expenses = dm.load_expenses()
            self.budget = dm.load_budget()
        except dm.DataFileError as error:
            messagebox.showerror("File error", str(error))

    def save_data(self):
        try:
            dm.save_expenses(self.expenses)
        except dm.DataFileError as error:
            messagebox.showerror("File error", str(error))

    # ----------------------------------------------------------
    # Building the screen
    # ----------------------------------------------------------
    def build_form(self):
        frame = ttk.LabelFrame(self.root, text="Expense details")
        frame.pack(fill="x", padx=10, pady=5)

        self.date_var = tk.StringVar(value=str(date.today()))
        self.category_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.amount_var = tk.StringVar()

        ttk.Label(frame, text="Date (YYYY-MM-DD)").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        ttk.Entry(frame, textvariable=self.date_var, width=15).grid(row=0, column=1, padx=5)
        ttk.Label(frame, text="Category").grid(row=0, column=2, padx=5, sticky="w")
        ttk.Entry(frame, textvariable=self.category_var, width=15).grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Description").grid(row=1, column=0, padx=5, pady=3, sticky="w")
        ttk.Entry(frame, textvariable=self.description_var, width=15).grid(row=1, column=1, padx=5)
        ttk.Label(frame, text="Amount").grid(row=1, column=2, padx=5, sticky="w")
        ttk.Entry(frame, textvariable=self.amount_var, width=15).grid(row=1, column=3, padx=5)

        buttons = ttk.Frame(frame)
        buttons.grid(row=2, column=0, columnspan=4, pady=5)
        ttk.Button(buttons, text="Add", command=self.add_expense).pack(side="left", padx=3)
        ttk.Button(buttons, text="Update", command=self.update_expense).pack(side="left", padx=3)
        ttk.Button(buttons, text="Delete", command=self.delete_expense).pack(side="left", padx=3)
        ttk.Button(buttons, text="Clear", command=self.clear_form).pack(side="left", padx=3)

    def build_filters(self):
        frame = ttk.LabelFrame(self.root, text="Search and filter")
        frame.pack(fill="x", padx=10, pady=5)

        self.search_var = tk.StringVar()
        self.filter_category_var = tk.StringVar()
        self.filter_month_var = tk.StringVar()

        ttk.Label(frame, text="Search").grid(row=0, column=0, padx=5, pady=3)
        ttk.Entry(frame, textvariable=self.search_var, width=14).grid(row=0, column=1)
        ttk.Label(frame, text="Category").grid(row=0, column=2, padx=5)
        self.category_box = ttk.Combobox(frame, textvariable=self.filter_category_var,
                                         width=12, state="readonly")
        self.category_box.grid(row=0, column=3)
        ttk.Label(frame, text="Month (YYYY-MM)").grid(row=0, column=4, padx=5)
        ttk.Entry(frame, textvariable=self.filter_month_var, width=10).grid(row=0, column=5)
        ttk.Button(frame, text="Apply", command=self.refresh_table).grid(row=0, column=6, padx=5)
        ttk.Button(frame, text="Reset", command=self.reset_filters).grid(row=0, column=7)

    def build_table(self):
        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "date", "category", "description", "amount")
        self.table = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        for name in columns:
            self.table.heading(name, text=name.title())
        self.table.column("id", width=40, anchor="center")
        self.table.column("date", width=100)
        self.table.column("category", width=120)
        self.table.column("description", width=250)
        self.table.column("amount", width=90, anchor="e")
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<<TreeviewSelect>>", self.on_row_selected)

        scrollbar = ttk.Scrollbar(frame, command=self.table.yview)
        scrollbar.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scrollbar.set)

    def build_bottom_bar(self):
        frame = ttk.LabelFrame(self.root, text="Budget and reports")
        frame.pack(fill="x", padx=10, pady=5)

        self.budget_var = tk.StringVar(value=str(self.budget) if self.budget else "")
        ttk.Label(frame, text="Monthly budget").pack(side="left", padx=5)
        ttk.Entry(frame, textvariable=self.budget_var, width=10).pack(side="left")
        ttk.Button(frame, text="Set", command=self.set_budget).pack(side="left", padx=3)
        ttk.Button(frame, text="Summary", command=self.show_summary).pack(side="left", padx=3)
        ttk.Button(frame, text="Category Chart", command=self.show_category_chart).pack(side="left", padx=3)
        ttk.Button(frame, text="Budget Chart", command=self.show_budget_chart).pack(side="left", padx=3)

    # ----------------------------------------------------------
    # Table handling
    # ----------------------------------------------------------
    def refresh_table(self):
        """Apply the search/filter boxes and redraw the table."""
        try:
            shown = dm.filter_expenses(self.expenses,
                                       self.filter_category_var.get(),
                                       self.filter_month_var.get())
            shown = dm.search_expenses(shown, self.search_var.get())
        except ValueError as error:
            messagebox.showerror("Invalid filter", str(error))
            return

        self.table.delete(*self.table.get_children())
        for item in shown:
            self.table.insert("", "end", values=(item["id"], item["date"], item["category"],
                                                 item["description"], f"{item['amount']:.2f}"))

        # keep the category drop-down up to date
        self.category_box["values"] = [""] + dm.get_categories(self.expenses)

    def reset_filters(self):
        self.search_var.set("")
        self.filter_category_var.set("")
        self.filter_month_var.set("")
        self.refresh_table()

    def on_row_selected(self, event):
        """Copy the clicked row into the form so it can be updated/deleted."""
        selection = self.table.selection()
        if not selection:
            return
        values = self.table.item(selection[0])["values"]
        self.selected_id = int(values[0])
        self.date_var.set(values[1])
        self.category_var.set(values[2])
        self.description_var.set(values[3])
        self.amount_var.set(values[4])

    def clear_form(self):
        self.selected_id = None
        self.date_var.set(str(date.today()))
        self.category_var.set("")
        self.description_var.set("")
        self.amount_var.set("")
        self.table.selection_remove(self.table.selection())

    # ----------------------------------------------------------
    # Add / Update / Delete buttons
    # ----------------------------------------------------------
    def add_expense(self):
        try:
            dm.add_expense(self.expenses, self.date_var.get(), self.category_var.get(),
                           self.description_var.get(), self.amount_var.get())
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return
        self.save_data()
        self.clear_form()
        self.refresh_table()
        self.check_budget_warning()

    def update_expense(self):
        if self.selected_id is None:
            messagebox.showinfo("Update", "Please click an expense in the table first.")
            return
        try:
            dm.update_expense(self.expenses, self.selected_id, self.date_var.get(),
                              self.category_var.get(), self.description_var.get(),
                              self.amount_var.get())
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return
        self.save_data()
        self.clear_form()
        self.refresh_table()
        self.check_budget_warning()

    def delete_expense(self):
        if self.selected_id is None:
            messagebox.showinfo("Delete", "Please click an expense in the table first.")
            return
        if not messagebox.askyesno("Delete", "Delete the selected expense?"):
            return
        try:
            dm.delete_expense(self.expenses, self.selected_id)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        self.save_data()
        self.clear_form()
        self.refresh_table()

    # ----------------------------------------------------------
    # Budget and reports
    # ----------------------------------------------------------
    def set_budget(self):
        try:
            self.budget = validate_budget(self.budget_var.get())
            dm.save_budget(self.budget)
        except ValueError as error:
            messagebox.showerror("Invalid budget", str(error))
            return
        except dm.DataFileError as error:
            messagebox.showerror("File error", str(error))
            return
        messagebox.showinfo("Budget", f"Monthly budget set to {self.budget:.2f}")

    def check_budget_warning(self):
        """Warn the user if this month's spending is above the budget."""
        this_month = str(date.today())[:7]
        status = analysis.budget_status(self.expenses, self.budget, this_month)
        if status["over_budget"]:
            messagebox.showwarning("Budget exceeded",
                                   f"You have spent {status['spent']:.2f} this month, "
                                   f"which is above your budget of {status['budget']:.2f}.")

    def show_summary(self):
        """Open a window with totals, category summary and budget deviations."""
        if not self.expenses:
            messagebox.showinfo("Summary", "No expenses recorded yet.")
            return

        this_month = str(date.today())[:7]
        status = analysis.budget_status(self.expenses, self.budget, this_month)

        text = f"Total spent (all time): {analysis.total_spent(self.expenses):.2f}\n"
        text += f"\n--- This month ({this_month}) ---\n"
        text += f"Spent: {status['spent']:.2f}\n"
        if self.budget > 0:
            text += f"Budget: {status['budget']:.2f}\n"
            text += f"Remaining: {status['remaining']:.2f}  ({status['percent_used']}% used)\n"
        else:
            text += "No monthly budget set.\n"

        text += "\n--- Category totals ---\n"
        text += analysis.category_summary(self.expenses).to_string(index=False)

        text += "\n\n--- Major spending areas (top 3) ---\n"
        text += analysis.major_spending_areas(self.expenses).to_string(index=False)

        text += "\n\n--- Budget deviation per month (budget - spent) ---\n"
        text += analysis.monthly_summary(self.expenses, self.budget).to_string(index=False)

        window = tk.Toplevel(self.root)
        window.title("Summary")
        box = tk.Text(window, width=70, height=30, font=("Courier", 10))
        box.insert("1.0", text)
        box.config(state="disabled")
        box.pack(padx=10, pady=10)

    # ----------------------------------------------------------
    # Charts
    # ----------------------------------------------------------
    def show_category_chart(self):
        self.show_chart(charts.category_pie_chart(self.expenses), "Category Chart")

    def show_budget_chart(self):
        self.show_chart(charts.monthly_budget_chart(self.expenses, self.budget), "Budget Chart")

    def show_chart(self, figure, title):
        """Show a Matplotlib figure in a new window with a Save button."""
        window = tk.Toplevel(self.root)
        window.title(title)
        canvas = FigureCanvasTkAgg(figure, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        ttk.Button(window, text="Save as image",
                   command=lambda: self.save_chart(figure)).pack(pady=5)

    def save_chart(self, figure):
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG image", "*.png")])
        if not path:
            return
        try:
            figure.savefig(path)
            messagebox.showinfo("Saved", f"Chart saved to {path}")
        except OSError as error:
            messagebox.showerror("Error", f"Could not save the chart: {error}")
