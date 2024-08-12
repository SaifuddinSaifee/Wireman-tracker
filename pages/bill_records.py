# File: pages/bill_records.py

import streamlit as st
import pandas as pd
from database.connection import get_db
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from services import bill_records_service
from utils.helpers import format_currency, format_date
import logging

logging.basicConfig(filename='app.log', level=logging.ERROR)


def safe_float(value):
    try:
        return float(value) if value is not None else 0.0
    except:
        return 0.0


def bill_records():
    st.title("Bill Records")

    try:
        db = next(get_db())

        # Display total bill amount
        total_bill_amount = bill_records_service.get_total_bill_amount(db)
        st.metric("Total Bill Amount Generated", format_currency(total_bill_amount))

        # Get all bills and wiremen
        bills = bill_records_service.get_all_bills(db)
        wiremen = bill_records_service.get_all_wiremen(db)

        # Create a DataFrame for easy filtering
        df = pd.DataFrame([
            {
                "Bill ID": bill.id,
                "Wireman": next((w.name for w in wiremen if w.id == bill.wireman_id), "Unknown"),
                "Client Name": bill.client_name or "",
                "Amount": safe_float(bill.amount),
                "Date": bill.date or pd.NaT,
                "Points Earned": safe_float(bill.points_earned),
                "Payment Status": bill.payment_status or ""
            } for bill in bills
        ])

        # Filters
        st.header("Filter Bills")
        col1, col2 = st.columns(2)
        with col1:
            wireman_filter = st.multiselect("Wireman", options=["All"] + list(df["Wireman"].unique()))
            client_filter = st.text_input("Client Name (Fuzzy Search)")
        with col2:
            date_range = st.date_input("Date Range", value=(None, None))
            amount_range = st.slider("Bill Amount Range",
                                     float(df["Amount"].min()),
                                     float(df["Amount"].max()),
                                     (float(df["Amount"].min()), float(df["Amount"].max())))

        # Apply filters
        filtered_df = df.copy()
        if wireman_filter and "All" not in wireman_filter:
            filtered_df = filtered_df[filtered_df["Wireman"].isin(wireman_filter)]
        if client_filter:
            filtered_df = filtered_df[filtered_df["Client Name"].str.contains(client_filter, case=False, na=False)]
        if date_range[0] is not None:
            filtered_df = filtered_df[filtered_df["Date"].notnull() & (filtered_df["Date"] >= date_range[0])]
        if date_range[1] is not None:
            filtered_df = filtered_df[filtered_df["Date"].notnull() & (filtered_df["Date"] <= date_range[1])]
        filtered_df = filtered_df[
            (filtered_df["Amount"] >= amount_range[0]) & (filtered_df["Amount"] <= amount_range[1])]

        # Display filtered bills
        st.header("Bill Records")
        st.dataframe(filtered_df.style.format({
            "Amount": "{:.2f}",
            "Points Earned": "{:.2f}",
            "Date": lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else ""
        }))

        # Update and Delete functionality
        st.header("Update or Delete Bill")
        selected_bill_id = st.number_input("Enter Bill ID to Update/Delete", min_value=1, step=1)
        action = st.radio("Choose Action", ["Update", "Delete"])

        if action == "Update":
            update_bill(db, selected_bill_id, filtered_df)
        else:
            delete_bill(db, selected_bill_id)

    except Exception as e:
        logging.error(f"An error occurred in bill_records: {str(e)}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")


def update_bill(db: Session, bill_id: int, df: pd.DataFrame):
    bill_data = df[df["Bill ID"] == bill_id].to_dict('records')
    if bill_data:
        bill_data = bill_data[0]
        with st.form("update_bill"):
            client_name = st.text_input("Client Name", value=bill_data["Client Name"])
            amount = st.number_input("Amount", value=float(bill_data["Amount"]), min_value=0.0, step=100.0)
            bill_date = st.date_input("Bill Date",
                                      value=bill_data["Date"] if pd.notnull(bill_data["Date"]) else date.today())
            payment_status = st.selectbox("Payment Status", ["Paid", "Partially Paid", "Not paid"],
                                          index=["Paid", "Partially Paid", "Not paid"].index(
                                              bill_data["Payment Status"]) if bill_data["Payment Status"] in ["Paid",
                                                                                                              "Partially Paid",
                                                                                                              "Not paid"] else 0)

            if st.form_submit_button("Update Bill"):
                success, message = bill_records_service.update_bill(
                    db, bill_id, client_name, Decimal(str(amount)), bill_date, payment_status
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
    else:
        st.error("Bill not found.")


def delete_bill(db: Session, bill_id: int):
    if st.button(f"Delete Bill {bill_id}"):
        success, message = bill_records_service.delete_bill(db, bill_id)
        if success:
            st.success(message)
        else:
            st.error(message)


if __name__ == "__main__":
    bill_records()