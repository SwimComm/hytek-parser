from __future__ import annotations

from datetime import date, datetime

import attr

from .enums import Course, Gender, MeetType


@attr.s(auto_attribs=True)
class Software:
    """Represents a Hytek software version."""

    name: str
    version: str


@attr.s(auto_attribs=True, init=False)
class Meet:
    """Represents a swim meet.

    Altitude is measured in meters.
    """

    # Primary info
    name: str
    facility: str
    start_date: date
    end_date: date
    altitude: int
    country: str

    # Secondary info
    masters: bool
    type_: MeetType
    course: Course

    # Entries
    teams: dict[str, Team]
    swimmers: dict[int, Swimmer]

    def add_swimmer(self, swimmer: Swimmer) -> None:
        """Add a swimmer to the meet."""
        self.swimmers[swimmer.meet_id] = swimmer
        self.teams[swimmer.team_code].swimmers[swimmer.meet_id] = swimmer

    def get_last_team(self) -> tuple[str, Team]:
        """Get the last team added as (team_code, Team)."""
        return list(self.teams.items())[-1]


@attr.s(auto_attribs=True, init=False)
class Team:
    """Represents a swim team."""

    # Identification
    code: str
    name: str
    short_name: str

    # Location
    address_1: str
    address_2: str
    city: str
    state: str
    zip_code: str
    country: str
    region: str

    # Swimmers
    swimmers: dict[int, Swimmer]


@attr.s(auto_attribs=True, init=False)
class Swimmer:
    """Represents a swimmer in a meet."""

    # Biological info? If you have a better name tell me.
    gender: Gender
    date_of_birth: date
    age: int

    # Names
    first_name: str
    last_name: str
    nick_name: str
    middle_initial: str

    # ID numbers
    meet_id: int
    team_id: int
    usa_swimming_id: str
    team_code: str


@attr.s(auto_attribs=True, init=False)
class ParsedHytekFile:
    """Represents a parsed Hytek file."""

    # File info
    file_description: str
    software: Software
    date_created: datetime
    licensee: str

    # Meet info
    meet: Meet
