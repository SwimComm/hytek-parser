from datetime import datetime
from typing import Any

from loguru import logger

from ...schemas import Gender, ParsedHytekFile, Swimmer
from .._utils import extract


def d1_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a D1 swimmer entry line."""
    team_code, _ = file.meet.get_last_team()
    swimmer = Swimmer()

    try:
        swimmer.gender = Gender(extract(line, 3, 1))
    except ValueError:
        logger.exception("Error in parsing gender.")
        swimmer.gender = Gender.PARSING_ERROR

    swimmer.meet_id = int(extract(line, 4, 5))

    swimmer.last_name = extract(line, 9, 20)
    swimmer.first_name = extract(line, 29, 20)
    swimmer.nick_name = extract(line, 49, 20)
    swimmer.middle_initial = extract(line, 69, 1)

    swimmer.usa_swimming_id = extract(line, 70, 14)
    if team_id := extract(line, 84, 5):
        swimmer.team_id = int(team_id)

    swimmer.date_of_birth = datetime.strptime(extract(line, 89, 8), "%m%d%Y").date()
    swimmer.age = int(extract(line, 97, 3))

    swimmer.team_code = team_code

    file.meet.add_swimmer(swimmer)
    return file
