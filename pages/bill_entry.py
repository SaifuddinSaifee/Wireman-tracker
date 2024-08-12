# File: pages/bill_entry_service.py

import streamlit as st
from database.connection import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from decimal import Decimal
from services import bill_entry_service


def bill_entry():
    """Streamlit page for bill entry."""
    st.title("Bill Entry")

    try:
        db = next(get_db())

        wiremen = bill_entry_service.fetch_all_wiremen(db)
        if not wiremen:
            st.warning("No wiremen registered yet. Please register a wireman before entering bills.")
            return

        with st.form("bill_entry_form"):
            wireman_name = st.selectbox("Wireman", options=[w.name for w in wiremen])
            client_name = st.text_input("Client Name")
            bill_amount = st.number_input("Bill Amount", min_value=0.0, step=100.0)
            bill_date = st.date_input("Bill Date", value=date.today())
            payment_status = st.selectbox("Payment Status", ["Paid", "Partially Paid", "Not paid"])

            submit_button = st.form_submit_button("Submit Bill")

        if submit_button:
            process_bill_submission(db, wireman_name, client_name, bill_amount, bill_date, payment_status)

    except SQLAlchemyError as e:
        st.error(f"An error occurred while connecting to the database: {str(e)}")


def process_bill_submission(db: Session, wireman_name: str, client_name: str, bill_amount: float, bill_date: date,
                            payment_status: str):
    """Process the bill submission."""
    is_valid, error_message = bill_entry_service.validate_bill_data(client_name, Decimal(str(bill_amount)))

    if not is_valid:
        st.error(error_message)
        return

    wireman = next((w for w in bill_entry_service.fetch_all_wiremen(db) if w.name == wireman_name), None)
    if not wireman:
        st.error("Selected wireman not found.")
        return

    success, message = bill_entry_service.submit_bill(
        db,
        wireman.id,
        client_name,
        Decimal(str(bill_amount)),
        bill_date,
        payment_status
    )

    if success:
        st.success(message)
    else:
        st.error(message)


if __name__ == "__main__":
    bill_entry()