import re
from typing import Any

from loguru import logger

from ...schemas import ParsedHytekFile, Team
from .._utils import extract

TEAM_CODE_REGEX = re.compile(r"\b(\w\w)")


def c1_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a C1 team ID line."""
    team = Team()

    team.name = extract(line, 8, 30)
    team.short_name = extract(line, 38, 16)

    if raw_team_code := extract(line, 3, 5):
        # Team code exists
        team.code = raw_team_code
    else:
        # Generate our own team code
        logger.warning(f"No team code found for team {team.name}, generating.")

        # Join first two letters of each work of uppercased full team name
        # Then truncate to 5 chars
        team.code = "".join(TEAM_CODE_REGEX.findall(team.name.upper()))[:5]

    file.meet.teams[team.code] = team
    return file


def c2_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a C2 team entry line."""
    # Get the last team
    team_code, team = file.meet.get_last_team()

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

    file.meet.teams[team_code] = team
    return file
