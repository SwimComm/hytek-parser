from datetime import datetime
from typing import Any

from ...schemas import Meet, ParsedHytekFile
from .._utils import MEET_COURSES, MEET_TYPES, extract


def b1_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a B1 primary meet info line."""
    meet = Meet()

    meet.name = extract(line, 3, 45)
    meet.facility = extract(line, 48, 45)
    meet.start_date = datetime.strptime(extract(line, 93, 8), "%m%d%Y").date()
    meet.end_date = datetime.strptime(extract(line, 101, 8), "%m%d%Y").date()
    meet.altitude = int(extract(line, 117, 5))
    # TODO: Find meet country
    meet.country = opts["default_country"]

    file.meet = meet
    return file


def b2_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a B2 secondary meet info line."""
    meet = file.meet

    meet.masters = extract(line, 94, 2) == "06"
    meet.type_code = extract(line, 97, 2)
    meet.type_ = MEET_TYPES[meet.type_code]
    meet.course = MEET_COURSES[extract(line, 99, 1)]

    file.meet = meet
    return file
