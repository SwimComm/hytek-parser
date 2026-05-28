import re
from typing import Any

from hytek_parser._utils import extract
from hytek_parser.hy3.schemas import ParsedHytekFile

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
        # logger.warning(f"No team code found for team {team_name}, generating.")

        # Join first two letters of each word of uppercased full team name
        # Then truncate to 5 chars
        team_code = "".join(TEAM_CODE_REGEX.findall(team_name.upper()))[:5]

    # LSC code at C1 cols 54-55 (2 chars, e.g. 'NE', 'PC', 'CA');
    # populates the previously-unset Team.region field.
    # Bug fix: was extract(54, 3), which grabbed the first letter of the contact
    # name at col 56, corrupting ~19% of teams' LSC codes.
    region = extract(line, 54, 2) or None

    # C1 contact name slots: cols 56-85 (contact_name_1) and 86-115 (contact_name_2).
    # Often identical; blank slot → None.
    contact_name_1 = extract(line, 56, 30) or None
    contact_name_2 = extract(line, 86, 30) or None

    file.meet.get_or_create_team(
        name=team_name,
        short_name=team_short_name,
        code=team_code,
        region=region,
        contact_name_1=contact_name_1,
        contact_name_2=contact_name_2,
    )
    return file


def c2_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a C2 team entry line."""
    # Get the last team
    team_code, team = file.meet.last_team

    # C2 has two 30-char address lines: line 1 (cols 3-32) is a free-text
    # "c/o"/attention line (often a contact person, sometimes the org), line 2
    # (cols 33-62) is the street. They were previously read as one 60-char blob.
    team.address_1 = extract(line, 3, 30)
    team.address_2 = extract(line, 33, 30)
    team.city = extract(line, 63, 30)
    team.state = extract(line, 93, 2)
    team.zip_code = extract(line, 95, 10)

    if team_country := extract(line, 105, 3):
        team.country = team_country
    else:
        team.country = opts["default_country"]

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
