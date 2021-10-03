from typing import Any

from loguru import logger


def extract(string: str, start: int, len_: int) -> str:
    """Extract a section of a certain length from a string.

    Args:
        string (str): The string to extract from.
        start (int): How many chars to move forward.
        len_ (int): The amount of chars to extract.

    Returns:
        str: The extracted string.
    """
    start -= 1
    return string[start : start + len_].rstrip()


def select_from_enum(enum: Any, value: Any) -> Any:
    """Safely select a value from an enum.

    Args:
        enum (BaseEnum): The enum to select the value from.
        value (Any): The value to select.

    Returns:
        BaseEnum: The selected value from the enum.
    """
    try:
        return enum(value)
    except ValueError:
        logger.exception(f"Error getting value from Enum {enum}")
        return enum.UNKNOWN
