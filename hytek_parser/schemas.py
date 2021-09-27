from datetime import date, datetime

import attr

# from typing import Optional


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
