import pandas as pd


def categorize_transaction(description):

    description = description.upper()

    if "SWIGGY" in description or "ZOMATO" in description:
        return "Food"

    if "AMAZON" in description or "SHOPPING" in description:
        return "Shopping"

    if "UBER" in description or "OLA" in description:
        return "Transport"

    if "NETFLIX" in description:
        return "Entertainment"

    if "RELIANCE FRESH" in description:
        return "Groceries"

    if "ELECTRICITY" in description:
        return "Bills"

    if "SALARY" in description:
        return "Income"

    return "Other"


def analyze_transactions(df):

    # Add category
    df["Category"] = df["Description"].apply(
        categorize_transaction
    )

    # Calculate income
    income = df[df["Type"] == "Credit"]["Amount"].sum()

    # Calculate expenses
    expenses = df[df["Type"] == "Debit"]["Amount"].sum()

    # Calculate savings
    savings = income - expenses

    # Category-wise expenses
    category_summary = (
        df[df["Type"] == "Debit"]
        .groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    return {
        "income": float(income),
        "expenses": float(expenses),
        "savings": float(savings),
        "categories": category_summary.to_dict()
    }