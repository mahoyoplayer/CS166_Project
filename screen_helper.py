from decimal import Decimal, InvalidOperation
import questionary

def is_valid_price(value):
    if value is None:
        return False

    value = value.strip()

    try:
        price = Decimal(value)
    except InvalidOperation:
        return False

    # Reject NaN and Infinity
    if not price.is_finite():
        return False

    # Must be positive
    if price < Decimal("0"):
        return False

    exponent = price.as_tuple().exponent

    # Makes Pylance happy
    if not isinstance(exponent, int):
        return False

    # Must have at most 2 decimal places
    if exponent < -2:
        return False

    # Must fit NUMERIC(10,2)
    if price > Decimal("99999999.99"):
        return False

    return True

def optional_text(value):
    if value is None:
        return None

    value = value.strip()
    return value if value else None

def required_text(prompt):
    while True:
        value = questionary.text(prompt).ask()

        if value is None:
            return None

        value = value.strip()

        if value:
            return value

        questionary.print("This field is required.", style="bold")
