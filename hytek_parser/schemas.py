from collections import defaultdict
from datetime import date, datetime

import attr

# from typing import Optional

_MEET_TYPES: dict[str, str] = {
    "00": "Time Trials",
    "01": "Invitational",
    "02": "Regional",
    "03": "LSC Championship",
    "04": "Zone",
    "05": "Zone Championship",
    "06": "National Championship",
    "07": "Juniors",
    "08": "Seniors",
    "09": "Dual",
    "0A": "International",
    "0B": "Open",
    "0C": "League",
}
MEET_TYPES: defaultdict[str, str] = defaultdict(lambda: "Unknown", _MEET_TYPES)

_MEET_COURSES: dict[str, str] = {
    # SCM
    "1": "SCM",
    "M": "SCM",
    # SCY
    "2": "SCY",
    "Y": "SCY",
    # LCM
    "3": "LCM",
    "L": "LCM",
    # Other
    "X": "Disqualified",
}
MEET_COURSES: defaultdict[str, str] = defaultdict(lambda: "Unknown", _MEET_COURSES)


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
    type_code: str
    type_: str
    course: str


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
