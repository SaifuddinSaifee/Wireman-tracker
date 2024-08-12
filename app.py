# File: app.py

import streamlit as st
from database.connection import get_db
from database.models import Wireman, Bill, Point
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from utils.helpers import format_currency

st.set_page_config(page_title="Referral Management System", page_icon="📊", layout="wide")

def main():
    """Main function to run the Streamlit app."""
    st.title("Referral Management System")

    st.write("""
    Welcome to the Referral Management System. Use the sidebar to navigate between different pages:
    - Bill Entry
    - Wireman Management
    - Bill Records
    """)

    try:
        db = next(get_db())
        display_summary_metrics(db)
    except SQLAlchemyError as e:
        st.error(f"An error occurred while connecting to the database: {str(e)}")

def display_summary_metrics(db: Session):
    """Display summary metrics on the main page."""
    try:
        total_wiremen = db.query(Wireman).count()
        total_bills = db.query(Bill).count()
        total_business = db.query(Bill.amount).all()
        total_business_amount = sum(amount for (amount,) in total_business)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Wiremen", total_wiremen)
        col2.metric("Total Bills", total_bills)
        col3.metric("Total Business", format_currency(total_business_amount))
    except SQLAlchemyError as e:
        st.error(f"An error occurred while fetching summary metrics: {str(e)}")

if __name__ == "__main__":
    main()