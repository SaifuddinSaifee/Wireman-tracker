# File: services/bill_entry_service.py

from sqlalchemy.orm import Session
from database.models import Wireman, Bill, Point
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from decimal import Decimal
from typing import List, Tuple


def fetch_all_wiremen(db: Session) -> List[Wireman]:
    """Fetch all wiremen from the database."""
    return db.query(Wireman).all()


def submit_bill(db: Session, wireman_id: int, client_name: str, bill_amount: Decimal, bill_date: date,
                payment_status: str) -> Tuple[bool, str]:
    """
    Submit a new bill and update points.

    Args:
        db (Session): The database session.
        wireman_id (int): The ID of the wireman.
        client_name (str): The name of the client.
        bill_amount (Decimal): The bill amount.
        bill_date (date): The date of the bill.
        payment_status (str): The payment status of the bill.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating success and a message.
    """
    try:
        points_earned = calculate_points(bill_amount)

        new_bill = Bill(
            wireman_id=wireman_id,
            client_name=client_name,
            amount=bill_amount,
            date=bill_date,
            payment_status=payment_status,
            points_earned=points_earned
        )
        db.add(new_bill)

        update_points(db, wireman_id, points_earned)

        db.commit()
        return True, f"Bill submitted successfully! {points_earned} points earned."
    except SQLAlchemyError as e:
        db.rollback()
        return False, f"An error occurred while submitting the bill: {str(e)}"


def calculate_points(amount: Decimal) -> Decimal:
    """Calculate points based on bill amount."""
    return amount // 1000


def update_points(db: Session, wireman_id: int, points_earned: Decimal):
    """Update points for the wireman."""
    point_record = db.query(Point).filter(Point.wireman_id == wireman_id).first()
    if point_record:
        point_record.total_points += points_earned
        point_record.balance_points += points_earned
    else:
        new_point_record = Point(
            wireman_id=wireman_id,
            total_points=points_earned,
            redeemed_points=Decimal('0'),
            balance_points=points_earned
        )
        db.add(new_point_record)


def validate_bill_data(client_name: str, bill_amount: Decimal) -> Tuple[bool, str]:
    """
    Validate bill entry data.

    Args:
        client_name (str): The name of the client.
        bill_amount (Decimal): The bill amount.

    Returns:
        Tuple[bool, str]: A tuple containing a boolean indicating if the data is valid,
                          and a string with an error message if not valid.
    """
    if not client_name:
        return False, "Client name is required."
    if bill_amount <= Decimal('0'):
        return False, "Bill amount must be greater than zero."
    return True, ""