# File: pages/wireman_management.py

import streamlit as st
from database.connection import get_db
from database.models import Wireman
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from utils.helpers import format_currency, format_date
from services import wireman_management_services


def wireman_management():
    """
    Streamlit page for managing wiremen, including registration, updates, and statistics.
    """
    st.title("Wireman Management")

    try:
        db = next(get_db())

        # Wireman management tabs
        st.header("Manage Wiremen")
        crud_tab, list_tab, leaderboard_tab, dashboard_tab = st.tabs(["CRUD Operations", "Wiremen List", "Leaderboard", "Wireman Dashboard"])

        with crud_tab:
            crud_operation = st.radio("Select Operation", ["Register New Wireman", "Update Wireman", "Delete Wireman"])

            if crud_operation == "Register New Wireman":
                register_wireman(db)
            elif crud_operation == "Update Wireman":
                update_wireman(db)
            else:  # Delete Wireman
                delete_wireman(db)

        with list_tab:
            display_wiremen_list(db)

        with leaderboard_tab:
            display_leaderboard(db)

        with dashboard_tab:
            display_wireman_dashboard_tab(db)

    except SQLAlchemyError as e:
        st.error(f"An error occurred while accessing the database: {str(e)}")


def register_wireman(db: Session):
    """Register a new wireman."""
    with st.form("register_wireman"):
        name = st.text_input("Name")
        contact_info = st.text_input("Contact Info")
        submit = st.form_submit_button("Register Wireman")

        if submit:
            success, message = wireman_management_services.register_new_wireman(db, name, contact_info)
            if success:
                st.success(message)
            else:
                st.error(message)


def update_wireman(db: Session):
    """Update wireman details."""
    wiremen = wireman_management_services.fetch_all_wiremen(db)
    selected_wireman = st.selectbox("Select Wireman to Update", options=[w.name for w in wiremen])

    if selected_wireman:
        wireman = next((w for w in wiremen if w.name == selected_wireman), None)
        if wireman:
            with st.form("update_wireman"):
                name = st.text_input("Name", value=wireman.name)
                contact_info = st.text_input("Contact Info", value=wireman.contact_info)
                submit = st.form_submit_button("Update Wireman")

                if submit:
                    success, message = wireman_management_services.update_wireman(db, wireman.id, name, contact_info)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        else:
            st.error("Selected wireman not found. Please refresh the page and try again.")


def delete_wireman(db: Session):
    """Delete a wireman."""
    wiremen = wireman_management_services.fetch_all_wiremen(db)
    selected_wireman = st.selectbox("Select Wireman to Delete", options=[w.name for w in wiremen])

    if selected_wireman:
        wireman = next((w for w in wiremen if w.name == selected_wireman), None)
        if wireman:
            if st.button(f"Delete {wireman.name}"):
                confirm = st.checkbox(
                    "I understand that this action cannot be undone and will delete all associated records.")
                if confirm:
                    success, message = wireman_management_services.delete_wireman(db, wireman.id)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please confirm the deletion by checking the box above.")
        else:
            st.error("Selected wireman not found. Please refresh the page and try again.")


def display_wiremen_list(db: Session):
    """Display list of wiremen with filtering options."""
    st.subheader("Wiremen List")
    filter_by = st.selectbox("Filter by", ["Balance Points", "Total Bill Amount"])
    min_value = st.number_input("Minimum Value", value=0.0, step=100.0)
    max_value = st.number_input("Maximum Value", value=10000.0, step=100.0)

    filter_key = "balance_points" if filter_by == "Balance Points" else "total_bill_amount"
    filtered_wiremen = wireman_management_services.get_wiremen_with_points_or_bills(db, filter_key, min_value, max_value)

    if filtered_wiremen:
        st.table(
            {
                "Wireman": [w.name for w, v in filtered_wiremen],
                filter_by: [format_currency(v) for w, v in filtered_wiremen]
            }
        )
    else:
        st.info("No wiremen found matching the criteria.")


def display_leaderboard(db: Session):
    """Display leaderboard based on selected category."""
    st.subheader("Leaderboard")
    leaderboard_category = st.selectbox(
        "Select Leaderboard Category",
        ["Total Bill Amount", "Number of Bills", "Balance Points", "Total Points Scored"]
    )

    category_key = leaderboard_category.lower().replace(" ", "_")
    leaderboard = wireman_management_services.get_leaderboard(db, category_key)

    if leaderboard:
        st.table(
            {
                "Rank": range(1, len(leaderboard) + 1),
                "Wireman": [w.name for w, v in leaderboard],
                leaderboard_category: [format_currency(v) if "amount" in category_key else v for w, v in leaderboard]
            }
        )
    else:
        st.info("No data available for the leaderboard.")

def display_wireman_dashboard_tab(db: Session):
    """Display the wireman dashboard in a tab."""
    wiremen = wireman_management_services.fetch_all_wiremen(db)
    if not wiremen:
        st.warning("No wiremen registered yet. Please register a wireman to view the dashboard.")
        return

    selected_wireman = st.selectbox("Select Wireman", options=[w.name for w in wiremen])

    if selected_wireman:
        wireman = next((w for w in wiremen if w.name == selected_wireman), None)
        if wireman:
            display_wireman_dashboard(db, wireman)
            manage_points(db, wireman)
        else:
            st.error("Selected wireman not found. Please refresh the page and try again.")

def display_wireman_dashboard(db: Session, wireman: Wireman):
    """Display dashboard for the selected wireman."""
    st.subheader(f"Dashboard for {wireman.name}")

    dashboard_data = wireman_management_services.get_wireman_dashboard_data(db, wireman.id)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Bills", dashboard_data["total_bills"])
    col2.metric("Total Business", format_currency(dashboard_data["total_business"]))
    col3.metric("Latest Bill Date",
                format_date(dashboard_data["latest_bill_date"]) if dashboard_data["latest_bill_date"] else "N/A")

    col4, col5 = st.columns(2)
    col4.metric("Total Points", float(dashboard_data["total_points"]))
    col5.metric("Balance Points", float(dashboard_data["balance_points"]))


def manage_points(db: Session, wireman: Wireman):
    """Manage points for the selected wireman."""
    st.subheader("Manage Points")

    point_record = wireman_management_services.get_point_record(db, wireman.id)
    if not point_record:
        st.warning("No points record found for this wireman.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Redeem All Points"):
            success, message = wireman_management_services.redeem_all_points(db, wireman.id)
            if success:
                st.success(message)
            else:
                st.error(message)

    with col2:
        with st.form("redeem_points"):
            points_to_redeem = st.number_input("Points to Redeem", min_value=0.0,
                                               max_value=float(point_record.balance_points), step=0.01)
            if st.form_submit_button("Redeem Points"):
                success, message = wireman_management_services.redeem_specific_points(db, wireman.id,
                                                                                      Decimal(str(points_to_redeem)))
                if success:
                    st.success(message)
                else:
                    st.error(message)

    with col3:
        if st.button("Reset All Points"):
            success, message = wireman_management_services.reset_points(db, wireman.id)
            if success:
                st.success(message)
            else:
                st.error(message)


if __name__ == "__main__":
    wireman_management()