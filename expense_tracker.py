import streamlit as st
import json
import os
from datetime import date
import pandas as pd
import plotly.express as px

FILE_NAME = "expenses.json"

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .summary-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #ddd;
        text-align: center;
        margin-bottom: 10px;
    }

    .summary-value {
        font-size: 28px;
        font-weight: bold;
    }

    .section-title {
        font-size: 25px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        border: 1px solid #ddd;
        padding: 15px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


def load_expenses():
    if not os.path.exists(FILE_NAME):
        return []

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_expenses(expenses):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=4)


if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None


st.markdown(
    '<div class="main-title">💰 Expense Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Track your expenses, savings and monthly financial activity</div>',
    unsafe_allow_html=True
)


menu = st.sidebar.radio(
    "📌 Navigation",
    [
        "🏠 Dashboard",
        "➕ Add Expense",
        "👀 View Expenses",
        "✏️ Edit Expense",
        "🗑️ Delete Expense",
        "📊 Charts & Analysis"
    ]
)


# =========================
# DASHBOARD
# =========================

if menu == "🏠 Dashboard":

    st.markdown(
        '<div class="section-title">📊 Expense Summary</div>',
        unsafe_allow_html=True
    )

    expenses = st.session_state.expenses

    if expenses:

        df = pd.DataFrame(expenses)

        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")

        total_expenses = df["Amount"].sum()

        current_month = date.today().strftime("%Y-%m")

        monthly_df = df[
            df["Date"].astype(str).str.startswith(current_month)
        ]

        monthly_expenses = monthly_df["Amount"].sum()

        if "Income" in df.columns:
            total_income = df["Income"].fillna(0).sum()
        else:
            total_income = 0

        savings = total_income - total_expenses

        if savings >= 0:
            financial_status = "💰 Money Saved"
        else:
            financial_status = "⚠️ Expenditure is Higher"

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "💸 Total Expenses",
            f"₹{total_expenses:,.2f}"
        )

        col2.metric(
            "📅 Monthly Expenses",
            f"₹{monthly_expenses:,.2f}"
        )

        col3.metric(
            "💰 Savings",
            f"₹{savings:,.2f}"
        )

        col4.metric(
            "📌 Status",
            financial_status
        )

        st.divider()

        st.markdown(
            '<div class="section-title">📅 Monthly Expense Overview</div>',
            unsafe_allow_html=True
        )

        df["Month"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        ).dt.strftime("%Y-%m")

        monthly_summary = (
            df.groupby("Month")["Amount"]
            .sum()
            .reset_index()
        )

        if not monthly_summary.empty:

            fig = px.bar(
                monthly_summary,
                x="Month",
                y="Amount",
                title="Monthly Expenses",
                labels={
                    "Month": "Month",
                    "Amount": "Expense Amount (₹)"
                }
            )

            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Amount (₹)",
                hovermode="x unified"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:

        st.info(
            "No expenses available yet. Add your first expense from the sidebar."
        )


# =========================
# ADD EXPENSE
# =========================

elif menu == "➕ Add Expense":

    st.markdown(
        '<div class="section-title">➕ Add New Expense</div>',
        unsafe_allow_html=True
    )

    with st.form("add_expense_form"):

        col1, col2 = st.columns(2)

        with col1:

            expense_date = st.date_input(
                "📅 Date",
                value=date.today()
            )

            category = st.selectbox(
                "📂 Category",
                [
                    "Food",
                    "Travel",
                    "Shopping",
                    "Education",
                    "Bills",
                    "Entertainment",
                    "Healthcare",
                    "Transportation",
                    "Other"
                ]
            )

            description = st.text_input(
                "📝 Description",
                placeholder="Enter expense description"
            )

        with col2:

            amount = st.number_input(
                "💰 Amount (₹)",
                min_value=0.0,
                step=100.0
            )

            income = st.number_input(
                "💵 Monthly Income (₹)",
                min_value=0.0,
                step=1000.0
            )

            payment_method = st.selectbox(
                "💳 Payment Method",
                [
                    "Cash",
                    "UPI",
                    "Debit Card",
                    "Credit Card",
                    "Net Banking",
                    "Other"
                ]
            )

        submitted = st.form_submit_button(
            "➕ Add Expense",
            use_container_width=True
        )

        if submitted:

            if amount <= 0:

                st.error(
                    "❌ Amount must be greater than ₹0."
                )

            elif not description.strip():

                st.error(
                    "❌ Please enter an expense description."
                )

            else:

                new_expense = {
                    "ID": len(st.session_state.expenses) + 1,
                    "Date": str(expense_date),
                    "Category": category,
                    "Description": description.strip(),
                    "Amount": amount,
                    "Income": income,
                    "Payment Method": payment_method
                }

                st.session_state.expenses.append(
                    new_expense
                )

                save_expenses(
                    st.session_state.expenses
                )

                st.success(
                    "✅ Expense added successfully!"
                )


# =========================
# VIEW EXPENSES
# =========================

elif menu == "👀 View Expenses":

    st.markdown(
        '<div class="section-title">👀 All Expenses</div>',
        unsafe_allow_html=True
    )

    expenses = st.session_state.expenses

    if expenses:

        df = pd.DataFrame(expenses)

        col1, col2 = st.columns(2)

        with col1:

            category_filter = st.multiselect(
                "📂 Filter by Category",
                options=sorted(df["Category"].unique())
            )

        with col2:

            search = st.text_input(
                "🔍 Search Description"
            )

        filtered_df = df.copy()

        if category_filter:

            filtered_df = filtered_df[
                filtered_df["Category"].isin(
                    category_filter
                )
            ]

        if search:

            filtered_df = filtered_df[
                filtered_df["Description"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

        st.info(
            f"Showing {len(filtered_df)} expense(s)."
        )

    else:

        st.warning(
            "No expenses found."
        )


# =========================
# EDIT EXPENSE
# =========================

elif menu == "✏️ Edit Expense":

    st.markdown(
        '<div class="section-title">✏️ Edit Expense</div>',
        unsafe_allow_html=True
    )

    expenses = st.session_state.expenses

    if not expenses:

        st.info(
            "No expenses available to edit."
        )

    else:

        expense_ids = [
            expense["ID"]
            for expense in expenses
        ]

        selected_id = st.selectbox(
            "Select Expense ID",
            expense_ids
        )

        selected_expense = next(
            expense
            for expense in expenses
            if expense["ID"] == selected_id
        )

        with st.form("edit_expense_form"):

            col1, col2 = st.columns(2)

            with col1:

                new_date = st.date_input(
                    "📅 Date",
                    value=pd.to_datetime(
                        selected_expense["Date"]
                    ).date()
                )

                new_category = st.selectbox(
                    "📂 Category",
                    [
                        "Food",
                        "Travel",
                        "Shopping",
                        "Education",
                        "Bills",
                        "Entertainment",
                        "Healthcare",
                        "Transportation",
                        "Other"
                    ],
                    index=[
                        "Food",
                        "Travel",
                        "Shopping",
                        "Education",
                        "Bills",
                        "Entertainment",
                        "Healthcare",
                        "Transportation",
                        "Other"
                    ].index(
                        selected_expense["Category"]
                    )
                )

                new_description = st.text_input(
                    "📝 Description",
                    value=selected_expense["Description"]
                )

            with col2:

                new_amount = st.number_input(
                    "💰 Amount (₹)",
                    min_value=0.0,
                    value=float(selected_expense["Amount"]),
                    step=100.0
                )

                new_income = st.number_input(
                    "💵 Monthly Income (₹)",
                    min_value=0.0,
                    value=float(
                        selected_expense.get(
                            "Income",
                            0
                        )
                    ),
                    step=1000.0
                )

                payment_methods = [
                    "Cash",
                    "UPI",
                    "Debit Card",
                    "Credit Card",
                    "Net Banking",
                    "Other"
                ]

                new_payment_method = st.selectbox(
                    "💳 Payment Method",
                    payment_methods,
                    index=payment_methods.index(
                        selected_expense.get(
                            "Payment Method",
                            "Cash"
                        )
                    )
                )

            update_button = st.form_submit_button(
                "💾 Update Expense",
                use_container_width=True
            )

            if update_button:

                if new_amount <= 0:

                    st.error(
                        "❌ Amount must be greater than ₹0."
                    )

                elif not new_description.strip():

                    st.error(
                        "❌ Description cannot be empty."
                    )

                else:

                    selected_expense["Date"] = str(
                        new_date
                    )

                    selected_expense["Category"] = (
                        new_category
                    )

                    selected_expense["Description"] = (
                        new_description.strip()
                    )

                    selected_expense["Amount"] = (
                        new_amount
                    )

                    selected_expense["Income"] = (
                        new_income
                    )

                    selected_expense[
                        "Payment Method"
                    ] = new_payment_method

                    save_expenses(
                        st.session_state.expenses
                    )

                    st.success(
                        "✅ Expense updated successfully!"
                    )


# =========================
# DELETE EXPENSE
# =========================

elif menu == "🗑️ Delete Expense":

    st.markdown(
        '<div class="section-title">🗑️ Delete Expense</div>',
        unsafe_allow_html=True
    )

    expenses = st.session_state.expenses

    if not expenses:

        st.info(
            "No expenses available to delete."
        )

    else:

        expense_ids = [
            expense["ID"]
            for expense in expenses
        ]

        selected_id = st.selectbox(
            "Select Expense ID",
            expense_ids
        )

        selected_expense = next(
            expense
            for expense in expenses
            if expense["ID"] == selected_id
        )

        st.warning(
            f"Selected Expense: "
            f"{selected_expense['Description']} — "
            f"₹{selected_expense['Amount']:,.2f}"
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this expense."
        )

        if st.button(
            "🗑️ Delete Expense",
            use_container_width=True
        ):

            if not confirm:

                st.error(
                    "❌ Please confirm deletion first."
                )

            else:

                st.session_state.expenses = [
                    expense
                    for expense in st.session_state.expenses
                    if expense["ID"] != selected_id
                ]

                save_expenses(
                    st.session_state.expenses
                )

                st.success(
                    "✅ Expense deleted successfully!"
                )

                st.rerun()


# =========================
# CHARTS & ANALYSIS
# =========================

elif menu == "📊 Charts & Analysis":

    st.markdown(
        '<div class="section-title">📊 Charts & Financial Analysis</div>',
        unsafe_allow_html=True
    )

    expenses = st.session_state.expenses

    if not expenses:

        st.info(
            "Add expenses to view charts and analysis."
        )

    else:

        df = pd.DataFrame(expenses)

        df["Amount"] = pd.to_numeric(
            df["Amount"],
            errors="coerce"
        )

        # Category Analysis

        st.subheader(
            "📂 Expenses by Category"
        )

        category_summary = (
            df.groupby("Category")["Amount"]
            .sum()
            .reset_index()
        )

        fig1 = px.pie(
            category_summary,
            names="Category",
            values="Amount",
            title="Expense Distribution by Category",
            hole=0.4
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

        # Monthly Analysis

        st.subheader(
            "📅 Monthly Expenses"
        )

        df["Month"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        ).dt.strftime("%Y-%m")

        monthly_summary = (
            df.groupby("Month")["Amount"]
            .sum()
            .reset_index()
        )

        fig2 = px.line(
            monthly_summary,
            x="Month",
            y="Amount",
            markers=True,
            title="Monthly Expense Trend"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # Payment Method

        st.subheader(
            "💳 Payment Method Analysis"
        )

        payment_summary = (
            df.groupby("Payment Method")["Amount"]
            .sum()
            .reset_index()
        )

        fig3 = px.bar(
            payment_summary,
            x="Payment Method",
            y="Amount",
            title="Expenses by Payment Method"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        # Financial Status

        st.subheader(
            "💰 Savings vs Expenditure"
        )

        total_expenses = df["Amount"].sum()

        total_income = df["Income"].fillna(0).sum()

        savings = total_income - total_expenses

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "💵 Total Income",
            f"₹{total_income:,.2f}"
        )

        col2.metric(
            "💸 Total Expenditure",
            f"₹{total_expenses:,.2f}"
        )

        col3.metric(
            "💰 Savings",
            f"₹{savings:,.2f}"
        )

        if savings > 0:

            st.success(
                f"💰 Money Saved: ₹{savings:,.2f}"
            )

        elif savings == 0:

            st.info(
                "⚖️ Income and expenditure are equal."
            )

        else:

            st.error(
                f"⚠️ Expenditure is higher than income by "
                f"₹{abs(savings):,.2f}"
            )

        # Export Data

        st.subheader(
            "📥 Export Expense Data"
        )

        json_data = json.dumps(
            st.session_state.expenses,
            indent=4
        )

        st.download_button(
            label="📥 Download Expenses as JSON",
            data=json_data,
            file_name="expenses.json",
            mime="application/json",
            use_container_width=True
        )