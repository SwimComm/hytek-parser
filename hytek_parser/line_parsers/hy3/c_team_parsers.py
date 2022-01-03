import re
from typing import Any

from loguru import logger

from ...schemas import ParsedHytekFile
from .._utils import extract

TEAM_CODE_REGEX = re.compile(r"\b(\w\w)")


def c1_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a C1 team ID line."""
    # Get team info
    team_name = extract(line, 8, 30)
    team_short_name = extract(line, 38, 16)

    if raw_team_code := extract(line, 3, 5):
        # Team code exists
        team_code = raw_team_code
    else:
        # Generate our own team code
        logger.warning(f"No team code found for team {team_name}, generating.")

        # Join first two letters of each work of uppercased full team name
        # Then truncate to 5 chars
        team_code = "".join(TEAM_CODE_REGEX.findall(team_name.upper()))[:5]

    file.meet.get_or_create_team(
        name=team_name, short_name=team_short_name, code=team_code
    )
    return file


def c2_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a C2 team entry line."""
    # Get the last team
    team_code, team = file.meet.last_team

    team.address_1 = extract(line, 3, 60)
    team.city = extract(line, 63, 30)
    team.state = extract(line, 93, 2)
    team.zip_code = extract(line, 95, 10)

    if team_country := extract(line, 105, 3):
        team.country = team_country
    else:
        team.country = opts["default_country"]

    # TODO: Team region
    team.region = "Unknown"

    file.meet.last_team = (team_code, team)
    return file


def c3_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a C2 team contact info line."""
    # Get the last team
    team_code, team = file.meet.last_team

    team.daytime_phone = extract(line, 33, 20) or "N/A"
    team.evening_phone = extract(line, 53, 20) or "N/A"
    team.fax = extract(line, 73, 20) or "N/A"
    team.email = extract(line, 93, 36) or "N/A"

    file.meet.last_team = team_code, team
    return file
