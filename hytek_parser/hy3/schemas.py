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

    # D1 fields previously dropped by the parser
    citizenship: Optional[str] = None
    # col 125; athlete status (Hytek MM "Status" field). Raw 1-char code — only
    # "N" (Normal) or blank observed across ~9.25M records; other GUI statuses
    # (Impaired/Exhibition/Foreigner/Rookie) never seen in data, so left as a
    # raw code rather than an enum.
    status: Optional[str] = None
    # cols 100-101; "Fr"/"So"/"Jr"/"Sr" school class in HS-meet exports,
    # other data / blank in club exports.
    class_year: Optional[str] = None


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
    region: Optional[str]

    # Contact info
    daytime_phone: str
    evening_phone: str
    fax: str
    email: str
    contact_name_1: Optional[str] = None
    contact_name_2: Optional[str] = None

    # Swimmers
    swimmers: dict[int, Swimmer] = Factory(dict)


@define
class DisqualificationInfo:
    """Information about an event disqualification."""

    code: DisqualificationCode
    info_str: Optional[str] = None
    info_str_detail: Optional[str] = None


@define(init=False)
class EventEntry:
    """Represents an entry in a meet event."""

    # Entry id info
    event_number: str
    swimmers: dict[int, Swimmer]
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
    # E2 fields previously dropped (pad + 3 buttons + backup_4 + alt code)
    prelim_pad_time: Optional[float] = None
    prelim_button_1_time: Optional[float] = None
    prelim_button_2_time: Optional[float] = None
    prelim_button_3_time: Optional[float] = None
    prelim_backup_4_time: Optional[float] = None
    # col 96; semantics unverified — observed 'A'/'K'/blank
    prelim_alt_time_code: Optional[str] = None

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
    # E2 fields previously dropped (pad + 3 buttons + backup_4 + alt code)
    swimoff_pad_time: Optional[float] = None
    swimoff_button_1_time: Optional[float] = None
    swimoff_button_2_time: Optional[float] = None
    swimoff_button_3_time: Optional[float] = None
    swimoff_backup_4_time: Optional[float] = None
    # col 96; semantics unverified — observed 'A'/'K'/blank
    swimoff_alt_time_code: Optional[str] = None

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
    # E2 fields previously dropped (pad + 3 buttons + backup_4 + alt code)
    finals_pad_time: Optional[float] = None
    finals_button_1_time: Optional[float] = None
    finals_button_2_time: Optional[float] = None
    finals_button_3_time: Optional[float] = None
    finals_backup_4_time: Optional[float] = None
    # col 96; semantics unverified — observed 'A'/'K'/blank
    finals_alt_time_code: Optional[str] = None

    # Relay attribution (moved from Event — set by f1_parser)
    relay_team_id: Optional[str] = None
    relay_swim_team_code: Optional[str] = None

    # Meet Division. The host-configured division label for the
    # entry: 'JV'/'VR' (varsity-style), classification codes ('A'/'AA'/'AAA'/'BB'),
    # HS enrollment classes ('5A'/'4A'/'3A'), age-group/level codes ('AG'/'SR'),
    # or numeric ('0'/'1'/'2'/'3'). Stored at cols 77-79 in most MM versions,
    # cols 92-93 in MM4/MM5-7.0Fa (read with col-77 precedence).
    meet_division: Optional[str] = None
    exhibition: bool = False

    def __init__(
        self,
        swimmers: dict[int, Swimmer],
        relay: bool,
        event_number: str,
        seed_time: Union[float, ReplacedTimeTimeCode],
        seed_course: Course,
        converted_seed_time: Union[float, ReplacedTimeTimeCode],
        converted_seed_time_course: Course,
        relay_team_id: Optional[str] = None,
        relay_swim_team_code: Optional[str] = None,
        meet_division: Optional[str] = None,
        exhibition: bool = False,
    ) -> None:
        self.swimmers = swimmers
        self.relay = relay
        self.event_number = event_number
        self.seed_time = seed_time
        self.seed_course = seed_course
        self.converted_seed_time = converted_seed_time
        self.converted_seed_time_course = converted_seed_time_course
        self.relay_team_id = relay_team_id
        self.relay_swim_team_code = relay_swim_team_code
        self.meet_division = meet_division
        self.exhibition = exhibition

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
            setattr(self, f"{course}_pad_time", None)
            setattr(self, f"{course}_button_1_time", None)
            setattr(self, f"{course}_button_2_time", None)
            setattr(self, f"{course}_button_3_time", None)
            setattr(self, f"{course}_backup_4_time", None)
            setattr(self, f"{course}_alt_time_code", None)

        self.prelim_dq_info = None
        self.swimoff_dq_info = None
        self.finals_dq_info = None

    def same_swimmer_entry_as(self, other: "EventEntry") -> bool:
        """Check if two entries are the same entry (so prelim+finals merge).

        For relays the identity is (event_number, relay_team_id,
        relay_swim_team_code, seed_time, seed_course) — not swimmers, which
        are populated later by F3.
        For individuals the identity is the existing (swimmers, event_number,
        seed_time, seed_course, converted_seed_time, converted_seed_time_course).
        """
        if self.relay or other.relay:
            return (
                self.relay == other.relay
                and self.relay_team_id == other.relay_team_id
                and self.relay_swim_team_code == other.relay_swim_team_code
                and self.event_number == other.event_number
                and self.seed_time == other.seed_time
                and self.seed_course == other.seed_course
            )
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
        swimmers: dict[int, Swimmer],
        relay: bool,
        event_number: str,
        seed_time: Union[float, ReplacedTimeTimeCode],
        seed_course: Course,
        converted_seed_time: Union[float, ReplacedTimeTimeCode],
        converted_seed_time_course: Course,
        relay_team_id: Optional[str] = None,
        relay_swim_team_code: Optional[str] = None,
        meet_division: Optional[str] = None,
        exhibition: bool = False,
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
            relay_team_id=relay_team_id,
            relay_swim_team_code=relay_swim_team_code,
            meet_division=meet_division,
            exhibition=exhibition,
        )
        if self.entries and self.entries[-1].same_swimmer_entry_as(entry):
            # P/F entries always listed together: a swimmer (individuals) or a
            # same-team relay (same team_id + letter) re-listed for finals.
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

    # Extended info (optional; populated by later parser stages). Kept at the
    # end of the field block (not next to `facility`/`country`) because attrs
    # forbids a defaulted field preceding the non-default fields above.
    sanction_number: Optional[str] = None
    notes: Optional[str] = None

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

    def get_or_create_team(
        self,
        name: str,
        short_name: str,
        code: str,
        region: Optional[str] = None,
        contact_name_1: Optional[str] = None,
        contact_name_2: Optional[str] = None,
    ) -> Team:
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
                region=region,
                state="N/A",
                zip_code="N/A",
                daytime_phone="N/A",
                evening_phone="N/A",
                fax="N/A",
                email="N/A",
                contact_name_1=contact_name_1,
                contact_name_2=contact_name_2,
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
