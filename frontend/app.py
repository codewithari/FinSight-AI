import streamlit as st
import pandas as pd
import requests

from backend.statement_reader import read_statement


# ============================================================
# Configuration
# ============================================================

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="FinSight AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# Custom CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main application */

    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }


    /* Hide Streamlit default menu */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* Header */

    .brand-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0;
        line-height: 1.2;
    }

    .brand-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
        margin-top: 0.2rem;
    }


    /* Local AI badge */

    .local-badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
    }


    /* Section titles */

    .section-title {
        font-size: 1.25rem;
        font-weight: 650;
        margin-top: 0.8rem;
        margin-bottom: 0.8rem;
    }


    /* AI insight card */

    .ai-card {
        padding: 1.25rem;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        background-color: #f9fafb;
        min-height: 250px;
    }


    .ai-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        color: #6b7280;
        text-transform: uppercase;
    }


    .ai-summary {
        font-size: 1rem;
        line-height: 1.6;
        margin-top: 0.6rem;
    }


    /* Status */

    .status {
        font-size: 0.82rem;
        color: #6b7280;
    }


    /* Footer */

    .app-footer {
        text-align: center;
        color: #9ca3af;
        font-size: 0.78rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #e5e7eb;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.markdown("## 💰 FinSight AI")

    st.caption("Local Personal Finance Analyst")

    st.divider()

    st.markdown("### 📄 Statement")

    uploaded_file = st.file_uploader(
        "Upload your bank or credit-card statement",
        type=["csv", "xlsx", "xls"],
        help="FinSight automatically detects the statement structure."
    )

    st.divider()

    st.markdown("### 🔒 Privacy")

    st.caption(
        "Your financial data is processed locally. "
        "AI insights are generated using your local Ollama model."
    )

    st.divider()

    st.markdown("### 🧠 Local AI")

    st.caption("Model: Qwen3:4B")
    st.caption("Runtime: Ollama")

    st.divider()

    st.caption("FinSight AI • Mini Project")


# ============================================================
# Header
# ============================================================

header_left, header_right = st.columns([5, 1], gap="large")

with header_left:

    st.markdown(
        '<div class="brand-title">FinSight AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-subtitle">'
        'Personal finance intelligence powered by local AI'
        '</div>',
        unsafe_allow_html=True
    )


with header_right:

    st.markdown(
        '<div style="text-align:right; margin-top:0.6rem;">'
        '<span class="local-badge">● Local AI</span>'
        '</div>',
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# Load Data
# ============================================================

if uploaded_file is not None:

    try:

        df = read_statement(uploaded_file)

        st.success(
            f"Statement loaded successfully • "
            f"{len(df)} transactions"
        )

    except Exception as e:

        st.error(
            f"Unable to read this statement: {e}"
        )

        st.stop()

else:

    df = pd.read_csv(
        "data/sample_transactions.csv"
    )


# ============================================================
# Validate Data
# ============================================================

required_columns = [
    "Date",
    "Description",
    "Amount",
    "Type"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    st.error(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )

    st.stop()


# ============================================================
# Analyze Button
# ============================================================

st.write("")

if st.button(
    "✨ Analyze My Finances",
    type="primary",
    width="stretch"
):

    transactions = []

    for _, row in df.iterrows():

        transactions.append(
            {
                "date": str(row["Date"]),
                "description": str(row["Description"]),
                "amount": float(row["Amount"]),
                "type": str(row["Type"])
            }
        )


    payload = {
        "transactions": transactions
    }


    try:

        # ---------------------------------------------
        # Financial analysis
        # ---------------------------------------------

        with st.spinner(
            "Analyzing your financial data..."
        ):

            response = requests.post(
                f"{API_URL}/analyze",
                json=payload,
                timeout=60
            )

            response.raise_for_status()

            result = response.json()


        st.session_state["analysis"] = result


        # ---------------------------------------------
        # Automatic AI analysis
        # ---------------------------------------------

        with st.spinner(
            "🤖 FinSight AI is generating your insights..."
        ):

            ai_response = requests.post(
                f"{API_URL}/ai-analysis",
                json={
                    "financial_summary": result
                },
                timeout=120
            )

            ai_response.raise_for_status()

            ai_result = ai_response.json()


        st.session_state["ai_analysis"] = ai_result

        st.session_state["analyzed"] = True

        st.success(
            "Financial analysis completed successfully."
        )


    except requests.exceptions.RequestException as e:

        st.error(
            f"Unable to connect to FinSight backend: {e}"
        )


# ============================================================
# Dashboard
# ============================================================

if st.session_state.get("analyzed", False):

    result = st.session_state["analysis"]

    income = result["income"]
    expenses = result["expenses"]
    savings = result["savings"]

    categories = result["categories"]


    # --------------------------------------------------------
    # Savings rate
    # --------------------------------------------------------

    if income > 0:

        savings_rate = (
            savings / income
        ) * 100

    else:

        savings_rate = 0


    st.divider()

    st.markdown(
        '<div class="section-title">'
        '📊 Financial Overview'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # KPI Cards
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "💵 Income",
            f"₹{income:,.0f}"
        )


    with col2:

        st.metric(
            "💸 Expenses",
            f"₹{expenses:,.0f}"
        )


    with col3:

        st.metric(
            "💰 Savings",
            f"₹{savings:,.0f}"
        )


    with col4:

        st.metric(
            "📈 Savings Rate",
            f"{savings_rate:.1f}%"
        )


    st.write("")


    # --------------------------------------------------------
    # Main Dashboard
    # --------------------------------------------------------

    chart_col, ai_col = st.columns(
        [1.15, 1],
        gap="large"
    )


    # ========================================================
    # Spending Chart
    # ========================================================

    with chart_col:

        st.markdown(
            '<div class="section-title">'
            '📈 Spending by Category'
            '</div>',
            unsafe_allow_html=True
        )


        category_df = pd.DataFrame(
            list(categories.items()),
            columns=[
                "Category",
                "Amount"
            ]
        )


        category_df = category_df.sort_values(
            "Amount",
            ascending=False
        )


        st.bar_chart(
            category_df.set_index("Category"),
            height=300
        )


        if not category_df.empty:

            top_category = category_df.iloc[0]

            st.caption(
                f"Highest spending: "
                f"**{top_category['Category']}** "
                f"— ₹{top_category['Amount']:,.0f}"
            )


    # ========================================================
    # AI Insights
    # ========================================================

    with ai_col:

        st.markdown(
            '<div class="section-title">'
            '🤖 FinSight AI Insights'
            '</div>',
            unsafe_allow_html=True
        )


        ai_result = st.session_state.get(
            "ai_analysis",
            {}
        )


        analysis_text = ai_result.get(
            "analysis",
            "AI analysis is not available."
        )


        with st.container(border=True):

            st.markdown(
                '<div class="ai-label">'
                'LOCAL AI ANALYSIS'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                analysis_text
            )


    # --------------------------------------------------------
    # Transactions
    # --------------------------------------------------------

    st.divider()


    st.markdown(
        '<div class="section-title">'
        '📋 Transaction Details'
        '</div>',
        unsafe_allow_html=True
    )


    display_df = df.copy()


    display_df["Amount"] = display_df[
        "Amount"
    ].apply(
        lambda x: f"₹{x:,.0f}"
    )


    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        height=300
    )


    # --------------------------------------------------------
    # Category Summary
    # --------------------------------------------------------

    with st.expander(
        "View category breakdown"
    ):

        summary_df = category_df.copy()

        summary_df["Amount"] = summary_df[
            "Amount"
        ].apply(
            lambda x: f"₹{x:,.0f}"
        )


        st.dataframe(
            summary_df,
            width="stretch",
            hide_index=True
        )


# ============================================================
# Initial State
# ============================================================

else:

    st.divider()

    st.markdown(
        """
        ### 👋 Welcome to FinSight AI

        Upload a transaction statement from the sidebar
        and click **✨ Analyze My Finances**.

        FinSight will automatically:

        **1.** Process your transactions using Python and Pandas

        **2.** Calculate your financial summary using FastAPI

        **3.** Analyze spending patterns using your local Qwen3 AI model

        **4.** Present the results in this dashboard
        """
    )


# ============================================================
# Footer
# ============================================================

st.markdown(
    """
    <div class="app-footer">
        🔒 Local-first financial analysis •
        Python • FastAPI • Pandas • Ollama • Qwen3 • Streamlit
    </div>
    """,
    unsafe_allow_html=True
)

