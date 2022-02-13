from typing import Optional

from attrs import define


@define
class EventResultEntry:
    """An event result entry."""

    place: int

    swimmer_name: Optional[str]
    swimmer_age: Optional[int]
    swimmer_team: Optional[str]

    seed_time: Optional[float]
    seed_time_extra: Optional[str]
    seed_time_qualifications: Optional[str]

    prelim_time: Optional[float]
    prelim_time_extra: Optional[str]
    prelim_time_qualifications: Optional[str]

    finals_time: Optional[float]
    finals_time_extra: Optional[str]
    finals_time_qualifications: Optional[str]


@define
class ParsedEventResultXlsFile:
    """A parsed Event Result XLS file."""

    event_name: str
    parsing_elements: tuple[str, ...]
    results: list[EventResultEntry]
