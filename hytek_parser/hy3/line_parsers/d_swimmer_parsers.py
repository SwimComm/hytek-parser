from typing import Any

from hytek_parser._utils import extract, select_from_enum, int_or_none, date_or_none
from hytek_parser.hy3.schemas import Gender, ParsedHytekFile, Swimmer


def d1_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a D1 swimmer entry line."""
    team_code, _ = file.meet.last_team
    swimmer = Swimmer()

    swimmer.gender = select_from_enum(Gender, extract(line, 3, 1))

    swimmer.meet_id = int(extract(line, 4, 5))

    swimmer.last_name = extract(line, 9, 20)
    swimmer.first_name = extract(line, 29, 20)
    swimmer.nick_name = extract(line, 49, 20)
    swimmer.middle_initial = extract(line, 69, 1)
    swimmer.usa_swimming_id = extract(line, 70, 14)
    swimmer.team_id = int_or_none(extract(line, 84, 5))
    swimmer.date_of_birth = date_or_none(extract(line, 89, 8))
    swimmer.age = int(extract(line, 97, 3))

    # previously dropped D1 fields. Capture both per spec.
    # citizenship: cols 113-115 (3 chars). Observed: 'USA' or blank.
    # status: col 125 (1 char). Athlete status; observed 'N' (Normal) or blank.
    swimmer.citizenship = extract(line, 113, 3) or None
    swimmer.status = extract(line, 125, 1) or None
    # class_year: cols 100-101 (2 chars). "Fr"/"So"/"Jr"/"Sr" school
    # class in HS-meet exports; other data / blank in club exports.
    swimmer.class_year = extract(line, 100, 2) or None

    swimmer.team_code = team_code

    file.meet.add_swimmer(swimmer)
    return file
