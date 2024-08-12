# File: utils/helpers.py

from datetime import date
from decimal import Decimal


def format_currency(amount: Decimal) -> str:
    """
    Format a number as Indian Rupees.

    Args:
        amount (Decimal): The amount to format.

    Returns:
        str: The formatted currency string.
    """
    return f"₹{float(amount):,.2f}"


def format_date(date_obj: date) -> str:
    """
    Format a date object as a string.

    Args:
        date_obj (date): The date to format.

    Returns:
        str: The formatted date string.
    """
    return date_obj.strftime("%d %b %Y") if date_obj else "N/A"


def validate_bill_data(wireman_name: str, client_name: str, bill_amount: Decimal) -> tuple[bool, str]:
    """
    Validate bill entry data.

    Args:
        wireman_name (str): The name of the wireman.
        client_name (str): The name of the client.
        bill_amount (Decimal): The bill amount.

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating if the data is valid,
                          and a string with an error message if not valid.
    """
    if not wireman_name:
        return False, "Wireman name is required."
    if not client_name:
        return False, "Client name is required."
    if bill_amount <= Decimal('0'):
        return False, "Bill amount must be greater than zero."
    return True, ""