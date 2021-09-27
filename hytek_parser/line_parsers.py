from datetime import datetime
from typing import Callable

from .schemas import Meet, ParsedHytekFile, Software


def _extract(string: str, start: int, len_: int) -> str:
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


def a1_parser(line: str, file: ParsedHytekFile) -> None:
    """Parse an A1 line with file info."""
    file.file_description = _extract(line, 5, 25)
    file.software = Software(_extract(line, 30, 15), _extract(line, 45, 10))

    # Add in a 0 to make the datetime library happy
    raw_date = _extract(line, 59, 17)
    if raw_date[9] == " ":
        raw_date = raw_date[:9] + "0" + raw_date[10:]

    file.date_created = datetime.strptime(raw_date, "%d%m%Y %I:%M %p")
    file.licensee = _extract(line, 76, 53)


def b1_parser(line: str, file: ParsedHytekFile) -> None:
    """Parse a B1 primary meet info line."""
    meet_name = _extract(line, 3, 45)
    meet_facility = _extract(line, 48, 45)
    meet_start_date = datetime.strptime(_extract(line, 93, 8), "%m%d%Y").date()
    meet_end_date = datetime.strptime(_extract(line, 101, 8), "%m%d%Y").date()
    meet_altitude = int(_extract(line, 117, 5))

    meet = Meet(meet_name, meet_facility, meet_start_date, meet_end_date, meet_altitude)
    file.meet = meet


LINE_PARSERS: dict[str, Callable[[str, ParsedHytekFile], None]] = {
    "A1": a1_parser,
    "B1": b1_parser,
}
