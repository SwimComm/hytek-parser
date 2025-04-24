from datetime import date, datetime
from typing import Optional, Union

from attrs import Factory, define, field

from hytek_parser.hy3.enums import (
    Course,
    DisqualificationCode,
    Gender,
    GenderAge,
    MeetType,
    ReplacedTimeTimeCode,
    Stroke,
    WithTimeTimeCode,
)


@define(init=False)
class Swimmer:
    """Represents a swimmer in a meet."""

    # Biological info? If you have a better name tell me.
    gender: Gender
    date_of_birth: date|None
    age: int

    # Names
    first_name: str
    last_name: str
    nick_name: str
    middle_initial: str

    # ID numbers
    meet_id: int  # ID in the meet database
    team_id: int|None  # ID in the team database
    usa_swimming_id: str
    team_code: str  # Team 5-letter code


@define
class Team:
    """Represents a swim team."""

    # Identification
    name: str
    short_name: str
    code: str

    # Location
    address_1: str
    address_2: str
    city: str
    state: str
    zip_code: str
    country: str
    region: str

    # Contact info
    daytime_phone: str
    evening_phone: str
    fax: str
    email: str

    # Swimmers
    swimmers: dict[int, Swimmer] = Factory(dict)


@define
class DisqualificationInfo:
    """Information about an event disqualification."""

    code: DisqualificationCode
    info_str: Optional[str] = None


@define(init=False)
class EventEntry:
    """Represents an entry in a meet event."""

    # Entry id info
    event_number: str
    swimmers: list[Swimmer]
    relay: bool

    # Seed time info
    seed_time: Union[float, ReplacedTimeTimeCode]
    seed_course: Course
    converted_seed_time: Union[float, ReplacedTimeTimeCode]
    converted_seed_time_course: Course

    # Prelim time info
    prelim_time: Optional[Union[float, ReplacedTimeTimeCode]] = None
    prelim_splits: dict[int, float] = Factory(dict)
    prelim_course: Optional[Course] = None
    prelim_time_code: Optional[WithTimeTimeCode] = None
    prelim_dq_info: Optional[DisqualificationInfo] = None
    prelim_heat: Optional[int] = None
    prelim_lane: Optional[int] = None
    prelim_heat_place: Optional[int] = None
    prelim_overall_place: Optional[int] = None
    prelim_date: Optional[date] = None

    # Swimoff Time info
    swimoff_time: Optional[Union[float, ReplacedTimeTimeCode]] = None
    swimoff_splits: dict[int, float] = Factory(dict)
    swimoff_course: Optional[Course] = None
    swimoff_time_code: Optional[WithTimeTimeCode] = None
    swimoff_dq_info: Optional[DisqualificationInfo] = None
    swimoff_heat: Optional[int] = None
    swimoff_lane: Optional[int] = None
    swimoff_heat_place: Optional[int] = None
    swimoff_overall_place: Optional[int] = None
    swimoff_date: Optional[date] = None

    # Finals time info
    finals_time: Optional[Union[float, ReplacedTimeTimeCode]] = None
    finals_splits: dict[int, float] = Factory(dict)
    finals_course: Optional[Course] = None
    finals_time_code: Optional[WithTimeTimeCode] = None
    finals_dq_info: Optional[DisqualificationInfo] = None
    finals_heat: Optional[int] = None
    finals_lane: Optional[int] = None
    finals_heat_place: Optional[int] = None
    finals_overall_place: Optional[int] = None
    finals_date: Optional[date] = None

    def __init__(
        self,
        swimmers: list[Swimmer],
        relay: bool,
        event_number: str,
        seed_time: Union[float, ReplacedTimeTimeCode],
        seed_course: Course,
        converted_seed_time: Union[float, ReplacedTimeTimeCode],
        converted_seed_time_course: Course,
    ) -> None:
        self.swimmers = swimmers
        self.relay = relay
        self.event_number = event_number
        self.seed_time = seed_time
        self.seed_course = seed_course
        self.converted_seed_time = converted_seed_time
        self.converted_seed_time_course = converted_seed_time_course

        for course in ("prelim", "swimoff", "finals"):
            setattr(self, f"{course}_time", None)
            setattr(self, f"{course}_splits", dict())
            setattr(self, f"{course}_course", None)
            setattr(self, f"{course}_time_code", None)
            setattr(self, f"{course}_dq_info", None)
            setattr(self, f"{course}_heat", None)
            setattr(self, f"{course}_lane", None)
            setattr(self, f"{course}_heat_place", None)
            setattr(self, f"{course}_overall_place", None)
            setattr(self, f"{course}_date", None)

        self.prelim_dq_info = None
        self.swimoff_dq_info = None
        self.finals_dq_info = None

    def same_swimmer_entry_as(self, other: "EventEntry") -> bool:
        """Check if two entries are for the same swimmer and event."""
        return (
            self.swimmers == other.swimmers
            and self.event_number == other.event_number
            and self.seed_time == other.seed_time
            and self.seed_course == other.seed_course
            and self.converted_seed_time == other.converted_seed_time
            and self.converted_seed_time_course == other.converted_seed_time_course
        )


@define
class Event:
    """Represents a meet event."""

    # ID info
    number: str
    distance: int
    stroke: Stroke
    course: Course
    date_: Optional[date]
    fee: float

    # Relay info - only set if relay = True
    relay: bool
    relay_team_id: Optional[str]
    relay_swim_team_code: Optional[str]

    # Swimmer info
    gender: Gender
    gender_age: GenderAge
    age_min: int
    age_max: int
    open_: bool

    # Entires
    entries: list[EventEntry] = Factory(list)

    def get_or_create_entry(
        self,
        swimmers: list[Swimmer],
        relay: bool,
        event_number: str,
        seed_time: Union[float, ReplacedTimeTimeCode],
        seed_course: Course,
        converted_seed_time: Union[float, ReplacedTimeTimeCode],
        converted_seed_time_course: Course,
    ) -> EventEntry:
        """Get an event entry or create one if needed."""
        entry = EventEntry(
            swimmers=swimmers,
            relay=relay,
            event_number=event_number,
            seed_time=seed_time,
            seed_course=seed_course,
            converted_seed_time=converted_seed_time,
            converted_seed_time_course=converted_seed_time_course,
        )
        if self.entries and self.entries[-1].same_swimmer_entry_as(entry):
            # P/F entries always listed together
            return self.entries[-1]
        else:
            # Create a new entry
            self.entries.append(entry)
            return entry

    @property
    def last_entry(self) -> EventEntry:
        """Get the last entry added to the event."""
        return self.entries[-1]

    @last_entry.setter
    def last_entry(self, entry: EventEntry) -> None:
        """Update the last entry."""
        self.entries[-1] = entry


@define(init=False)
class Meet:
    """Represents a swim meet.

    Altitude is measured in meters.
    """

    # Primary info
    name: str
    facility: str
    start_date: date
    end_date: date
    altitude: int|None
    country: str

    # Secondary info
    masters: bool
    type_: MeetType
    course: Course

    # Entries
    teams: dict[str, Team]
    swimmers: dict[int, Swimmer]
    events: dict[str, Event]

    # Bookeeping
    _last_team: tuple[str, Team] = field(default=None)
    _last_event: tuple[str, Event] = field(default=None)

    def __init__(self) -> None:
        self.teams = dict()
        self.swimmers = dict()
        self.events = dict()
        
        super(Meet, self).__init__()

    def add_swimmer(self, swimmer: Swimmer) -> None:
        """Add a swimmer to the meet."""
        if not self.swimmers.get(swimmer.meet_id):
            # Only add a swimmer if they don't exist
            self.swimmers[swimmer.meet_id] = swimmer
            self.teams[swimmer.team_code].swimmers[swimmer.meet_id] = swimmer

    def get_or_create_team(self, name: str, short_name: str, code: str) -> Team:
        """Get a team or create if needed."""
        if team := self.teams.get(code):
            return team
        else:
            team = Team(
                name=name,
                short_name=short_name,
                code=code,
                address_1="N/A",
                address_2="N/A",
                city="N/A",
                country="N/A",
                region="N/A",
                state="N/A",
                zip_code="N/A",
                daytime_phone="N/A",
                evening_phone="N/A",
                fax="N/A",
                email="N/A",
            )

            # Add team, this also updates the teams dict
            self.last_team = (code, team)
            return team

    @property
    def last_team(self) -> tuple[str, Team]:
        """Get the last team added as (team_code, Team)."""
        return self._last_team

    @last_team.setter
    def last_team(self, team_info: tuple[str, Team]) -> None:
        """Set the last team added."""
        self._last_team = team_info

        team_code, team = team_info
        self.teams[team_code] = team

    def get_or_create_event(
        self,
        number: str,
        distance: int,
        stroke: Stroke,
        course: Course,
        gender: Gender,
        gender_age: GenderAge,
        age_min: int,
        age_max: int,
        fee: float,
        relay: bool = False,
        relay_team_id: str|None = None,
        relay_swim_team_code: str|None = None,
    ) -> Event:
        """Get an event or create if needed."""
        if event := self.events.get(number):
            self._last_event = (number, event)
            return event
        else:
            open_event = age_min == 0 and age_max == 109

            event = Event(
                number=number,
                distance=distance,
                stroke=stroke,
                course=course,
                gender=gender,
                gender_age=gender_age,
                age_min=age_min,
                age_max=age_max,
                fee=fee,
                relay=relay,
                relay_team_id=relay_team_id,
                relay_swim_team_code=relay_swim_team_code,
                date_=None,
                open_=open_event,
            )

            # Add event, this also updates the events dict
            self.last_event = (number, event)
            return event

    @property
    def last_event(self) -> tuple[str, Event]:
        """Get the last defined event as (event_number, Event)."""
        return self._last_event

    @last_event.setter
    def last_event(self, event_info: tuple[str, Event]) -> None:
        """Set the last event."""
        self._last_event = event_info

        number, event = event_info
        self.events[number] = event


@define
class Software:
    """Represents a Hytek software version."""

    name: str
    version: str


@define(init=False)
class ParsedHytekFile:
    """Represents a parsed Hytek file."""

    # File info
    file_description: str
    software: Software
    date_created: datetime
    licensee: str

    # Meet info
    meet: Meet
