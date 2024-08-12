# File: pages/bill_records.py

import streamlit as st
import pandas as pd
from sqlalchemy import func
from database.connection import get_db
from database.models import Bill, Wireman
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from datetime import datetime, timedelta

def bill_records():
    st.title("Bill Records")

    try:
        db = next(get_db())

        # Display total bill amount
        total_bill_amount = get_total_bill_amount(db)
        st.metric("Total Bill Amount Generated", f"₹{total_bill_amount:,.2f}")

        # Get all wiremen for the filter
        wiremen = get_all_wiremen(db)
        wireman_names = ["All"] + [w.name for w in wiremen]

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            bill_id_filter = st.number_input("Filter by Bill ID (Optional)", min_value=0, value=0, step=1)
        with col2:
            wireman_filter = st.selectbox("Filter by Wireman", options=wireman_names)
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
                key="date_range"
            )

        # Get filtered bills
        bills = get_filtered_bills(db, bill_id_filter, wireman_filter, wiremen, date_range)

        # Create a DataFrame with filtered bills
        df = pd.DataFrame([
            {
                "Bill ID": bill.id,
                "Wireman": next((w.name for w in wiremen if w.id == bill.wireman_id), "Unknown"),
                "Client Name": bill.client_name,
                "Amount": float(bill.amount),
                "Date": bill.date,
                "Points Earned": float(bill.points_earned),
                "Payment Status": bill.payment_status
            } for bill in bills
        ])

        # Display filtered bills
        st.header("Bill Records")
        if df.empty:
            st.info("No bills found matching the criteria.")
        else:
            st.dataframe(df.style.format({
                "Amount": "₹{:.2f}",
                "Points Earned": "{:.2f}",
                "Date": lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else ""
            }))

    except SQLAlchemyError as e:
        st.error(f"An error occurred while accessing the database: {str(e)}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")

def get_total_bill_amount(db: Session) -> Decimal:
    """Get the total bill amount from all wiremen combined."""
    return db.query(func.sum(Bill.amount)).scalar() or Decimal('0')

def get_filtered_bills(db: Session, bill_id: int = 0, wireman_name: str = "All", wiremen: list = None, date_range: tuple = None):
    """Get bills filtered by ID, Wireman, and/or Date Range if provided, otherwise get all bills."""
    query = db.query(Bill)
    if bill_id > 0:
        query = query.filter(Bill.id == bill_id)
    if wireman_name != "All":
        wireman = next((w for w in wiremen if w.name == wireman_name), None)
        if wireman:
            query = query.filter(Bill.wireman_id == wireman.id)
    if date_range and len(date_range) == 2:
        start_date, end_date = date_range
        query = query.filter(Bill.date.between(start_date, end_date))
    return query.order_by(Bill.date.desc()).all()

def get_all_wiremen(db: Session):
    """Get all wiremen."""
    return db.query(Wireman).all()

if __name__ == "__main__":
    bill_records()