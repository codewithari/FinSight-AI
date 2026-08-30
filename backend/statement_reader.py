import pandas as pd


# ============================================================
# Public entry point
# ============================================================

def read_statement(uploaded_file):

    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return read_csv_statement(uploaded_file)

    if filename.endswith((".xlsx", ".xls")):
        return read_excel_statement(uploaded_file)

    raise ValueError(
        "Unsupported file format. Please upload CSV or Excel."
    )


# ============================================================
# Excel
# ============================================================

def read_excel_statement(uploaded_file):

    df = pd.read_excel(uploaded_file)

    return normalize_dataframe(df)


# ============================================================
# CSV
# ============================================================

def read_csv_statement(uploaded_file):

    # --------------------------------------------------------
    # Read raw bytes
    # --------------------------------------------------------

    raw_data = uploaded_file.getvalue()

    # --------------------------------------------------------
    # Detect encoding
    # --------------------------------------------------------

    encodings = [
        "utf-8-sig",
        "utf-8",
        "utf-16",
        "utf-16-le",
        "utf-16-be",
        "cp1252",
        "latin1"
    ]

    content = None
    detected_encoding = None

    for encoding in encodings:

        try:

            content = raw_data.decode(encoding)
            detected_encoding = encoding

            break

        except UnicodeDecodeError:

            continue

    if content is None:

        raise ValueError(
            "Unable to decode the statement file."
        )

    # --------------------------------------------------------
    # Split into lines
    # --------------------------------------------------------

    lines = content.splitlines()

    if not lines:

        raise ValueError(
            "The uploaded statement is empty."
        )

    # --------------------------------------------------------
    # Find transaction table
    # --------------------------------------------------------

    header_index = None

    for i, line in enumerate(lines):

        line_lower = line.lower()

        if (
            "transaction type" in line_lower
            and "description" in line_lower
            and "amt" in line_lower
        ):

            header_index = i

            break

    if header_index is None:

        raise ValueError(
            "Could not find the transaction table "
            "in the statement."
        )

    # --------------------------------------------------------
    # Parse transaction rows
    # --------------------------------------------------------

    transactions = []

    for line in lines[header_index + 1:]:

        line = line.strip()

        if not line:
            continue

        # This statement uses ~|~ as delimiter
        if "~|~" not in line:
            continue

        fields = line.split("~|~")

        # Expected:
        #
        # 0 = Transaction Type
        # 1 = Customer
        # 2 = Date
        # 3 = Description
        # 4 = Amount
        # 5 = Debit/Credit
        # 6 = Rewards
        #

        if len(fields) < 5:
            continue

        transaction_type = fields[0].strip()
        customer = fields[1].strip()
        date = fields[2].strip()
        description = fields[3].strip()
        amount = fields[4].strip()

        debit_credit = ""

        if len(fields) >= 6:

            debit_credit = fields[5].strip()

        rewards = ""

        if len(fields) >= 7:

            rewards = fields[6].strip()

        # ----------------------------------------------------
        # Clean amount
        # ----------------------------------------------------

        amount_clean = (
            amount
            .replace(",", "")
            .replace("₹", "")
            .strip()
        )

        try:

            amount_value = float(amount_clean)

        except ValueError:

            continue

        # ----------------------------------------------------
        # Determine transaction type
        # ----------------------------------------------------

        transaction_direction = (
            debit_credit
            if debit_credit
            else "Debit"
        )

        # ----------------------------------------------------
        # Store transaction
        # ----------------------------------------------------

        transactions.append(
            {
                "Date": date,
                "Description": description,
                "Amount": amount_value,
                "Type": transaction_direction,
                "Rewards": rewards
            }
        )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not transactions:

        raise ValueError(
            "No transactions could be identified "
            "in this statement."
        )

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame(transactions)

    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce",
        dayfirst=True
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce"
    )

    # Remove invalid rows

    df = df.dropna(
        subset=[
            "Date",
            "Amount"
        ]
    )

    df = df.reset_index(drop=True)

    return df


# ============================================================
# Generic DataFrame normalization
# ============================================================

def normalize_dataframe(df):

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # --------------------------------------------------------
    # Find common columns
    # --------------------------------------------------------

    date_column = find_column(
        df,
        [
            "date",
            "transaction date",
            "txn date"
        ]
    )

    description_column = find_column(
        df,
        [
            "description",
            "narration",
            "transaction description",
            "merchant"
        ]
    )

    amount_column = find_column(
        df,
        [
            "amount",
            "amt",
            "transaction amount"
        ]
    )

    # --------------------------------------------------------
    # Amount exists
    # --------------------------------------------------------

    if amount_column:

        result = pd.DataFrame()

        result["Date"] = df[date_column] if date_column else ""

        result["Description"] = (
            df[description_column]
            if description_column
            else ""
        )

        result["Amount"] = (
            df[amount_column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
        )

        result["Amount"] = pd.to_numeric(
            result["Amount"],
            errors="coerce"
        )

        result["Type"] = "Debit"

        result["Date"] = pd.to_datetime(
            result["Date"],
            errors="coerce",
            dayfirst=True
        )

        result = result.dropna(
            subset=["Amount"]
        )

        return result.reset_index(drop=True)

    raise ValueError(
        "Could not identify an Amount column "
        "or Debit/Credit columns in the statement."
    )


# ============================================================
# Find column
# ============================================================

def find_column(df, possible_names):

    for column in df.columns:

        normalized = (
            str(column)
            .strip()
            .lower()
        )

        for name in possible_names:

            if normalized == name.lower():

                return column

    return None