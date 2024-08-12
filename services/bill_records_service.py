# File: services/bill_records_services.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import Bill, Wireman, Point
from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

def get_total_bill_amount(db: Session) -> Decimal:
    """Get the total bill amount from all wiremen combined."""
    return db.query(func.sum(Bill.amount)).scalar() or Decimal('0')

def get_all_bills(db: Session) -> List[Bill]:
    """Get all bills ordered by date descending."""
    return db.query(Bill).order_by(Bill.date.desc()).all()

def get_all_wiremen(db: Session) -> List[Wireman]:
    """Get all wiremen."""
    return db.query(Wireman).all()

def update_bill(
    db: Session,
    bill_id: int,
    client_name: str,
    amount: Decimal,
    date: date,
    payment_status: str
) -> Tuple[bool, str]:
    """Update a bill and recalculate points."""
    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if not bill:
            return False, "Bill not found."

        old_points = bill.points_earned
        new_points = amount // 1000

        # Update bill
        bill.client_name = client_name
        bill.amount = amount
        bill.date = date
        bill.payment_status = payment_status
        bill.points_earned = new_points

        # Update points for wireman
        point_record = db.query(Point).filter(Point.wireman_id == bill.wireman_id).first()
        if point_record:
            point_record.total_points += (new_points - old_points)
            point_record.balance_points += (new_points - old_points)

        db.commit()
        return True, "Bill updated successfully."
    except Exception as e:
        db.rollback()
        return False, f"An error occurred: {str(e)}"

def delete_bill(db: Session, bill_id: int) -> Tuple[bool, str]:
    """Delete a bill and update points."""
    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if not bill:
            return False, "Bill not found."

        # Update points for wireman
        point_record = db.query(Point).filter(Point.wireman_id == bill.wireman_id).first()
        if point_record:
            point_record.total_points -= bill.points_earned
            point_record.balance_points -= bill.points_earned

        db.delete(bill)
        db.commit()
        return True, "Bill deleted successfully."
    except Exception as e:
        db.rollback()
        return False, f"An error occurred: {str(e)}"