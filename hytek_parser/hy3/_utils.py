from typing import Optional, Union

from hytek_parser._utils import safe_cast, select_from_enum
from hytek_parser.hy3.enums import ReplacedTimeTimeCode


def parse_time(raw_time: str) -> Union[float, ReplacedTimeTimeCode]:
    """Parse a time into either a number or time code.

    Args:
        raw_time (str): The time string extracted from the Hytek file.

    Returns:
        Union[float, ReplacedTimeTimeCode]: Either a numerical time or a time code.
    """
    if (casted := safe_cast(float, raw_time, default=-1)) != -1:
        # Number
        return casted
    else:
        return select_from_enum(ReplacedTimeTimeCode, raw_time)


def parse_time_or_none(raw_time: str) -> Optional[float]:
    """Parse a timing field where 0.00/blank means 'not recorded'.

    Unlike parse_time (which returns 0.0 for "0.00" and a ReplacedTimeTimeCode
    for blank/non-numeric input), this returns None unless the value is a
    positive float. Used for pad and backup-button times, where an unused
    slot is written as 0.00 and should surface as None rather than 0.0.
    """
    val = parse_time(raw_time)
    return val if isinstance(val, float) and val > 0.0 else None
