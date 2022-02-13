from typing import Union

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
