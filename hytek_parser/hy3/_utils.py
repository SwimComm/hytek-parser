import math
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


def parse_reaction_time(raw: str) -> Optional[float]:
    """Parse a reaction/takeoff-time column (E2 col 83-87, F2 col 83-102).

    NEGATIVE VALUES ARE MEANINGFUL and load-bearing here: a relay takeover slot
    records an early exchange as a negative number (7,868 values corpus-wide).
    ``parse_time_or_none`` requires > 0.0 and would silently destroy every one
    of them -- do not substitute it.

    Sentinels, all meaning "not recorded": blank, 0.00 in any sign spelling,
    and the literal NRT ("No Reaction Time") that Meet Manager writes into
    takeover slots when the exchange was not measured.

    Values above the plausible reaction range are returned unchanged. A
    minority of files put something else in these columns; its meaning is
    unresolved, and filtering it here would make it permanently invisible.
    """
    val = raw.strip()
    if not val or val.upper() == "NRT":
        return None
    try:
        num = float(val)
    except ValueError:
        # Observed malformed forms: a bare "+" sign, stray high bytes.
        return None
    if not math.isfinite(num):
        # float() accepts "nan"/"inf"/"-inf", all five characters or fewer,
        # so they fit this column like any other token. Neither is a
        # reaction time -- and a bare int() downstream would raise on them
        # (ValueError on nan, OverflowError on inf) instead of yielding None
        # like every other malformed token, dropping the whole file.
        return None
    # float() maps "0.00", "+0.00" and "-0.00" all to zero; all three are the
    # "not recorded" sentinel.
    return None if num == 0.0 else num
