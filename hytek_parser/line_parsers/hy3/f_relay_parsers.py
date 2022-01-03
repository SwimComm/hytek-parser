from datetime import datetime
from typing import Any, Optional

from ...enums import (
    Course,
    DisqualificationCode,
    GenderAge,
    ResultType,
    Stroke,
    WithTimeTimeCode,
)
from ...schemas import DisqualificationInfo, Gender, ParsedHytekFile, Swimmer
from .._utils import extract, get_age_group, parse_time, safe_cast, select_from_enum


def f1_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse an F1 relay event entry."""
    # Get team and relay ID
    team_code = extract(line, 3, 5)
    relay_team = extract(line, 8, 1)  # A, etc.

    # Get event info
    event_gender = select_from_enum(Gender, extract(line, 14, 1))
    event_gender_age = select_from_enum(GenderAge, extract(line, 15, 1))
    distance = safe_cast(int, extract(line, 16, 6))
    stroke = select_from_enum(Stroke, extract(line, 22, 1))

    # Have to set these now since swimmer ages are not available yet
    age_min = safe_cast(int, extract(line, 23, 3))
    age_max = safe_cast(int, extract(line, 26, 3))

    # Get last bits of event info
    event_fee = safe_cast(float, extract(line, 33, 6))
    event_number = safe_cast(int, extract(line, 39, 4))
    event_course = select_from_enum(Course, extract(line, 51, 1))

    # Get event
    event = file.meet.get_or_create_event(
        event_number,
        distance,
        stroke,
        event_course,
        event_gender,
        event_gender_age,
        age_min,
        age_max,
        event_fee,
        relay=True,
        relay_team_id=relay_team,
        relay_swim_team_code=team_code,
    )

    # Will populate this later
    entry_swimmers: list[Swimmer] = []

    # Event entry setup
    entry_event_number = event.number

    entry_seed_time = parse_time(extract(line, 52, 8))
    entry_seed_course = select_from_enum(Course, extract(line, 60, 1))

    entry_converted_seed_time = parse_time(extract(line, 43, 8))
    entry_converted_seed_time_course = event.course

    event.get_or_create_entry(
        swimmers=entry_swimmers,
        relay=True,
        event_number=entry_event_number,
        seed_time=entry_seed_time,
        seed_course=entry_seed_course,
        converted_seed_time=entry_converted_seed_time,
        converted_seed_time_course=entry_converted_seed_time_course,
    )

    # Update event
    file.meet.last_event = (event_number, event)

    return file


def f2_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse an F2 relay event result."""
    event_type = select_from_enum(ResultType, extract(line, 3, 1))

    time = parse_time(extract(line, 4, 8))
    course = select_from_enum(Course, extract(line, 12, 1))
    time_code = select_from_enum(WithTimeTimeCode, extract(line, 13, 1))

    dq_info = None
    if WithTimeTimeCode.is_dq_code(time_code):
        # Get the DQ code
        dq_code = select_from_enum(DisqualificationCode, extract(line, 14, 2))
        dq_info = DisqualificationInfo(dq_code, None)

    heat = safe_cast(int, extract(line, 21, 3))
    lane = safe_cast(int, extract(line, 24, 3))
    heat_place = safe_cast(int, extract(line, 27, 3))
    overall_place = safe_cast(int, extract(line, 30, 4))

    # Skipping over pad/plunger times since they are not that useful
    date_ = datetime.strptime(extract(line, 103, 8), "%m%d%Y").date()

    # Get entry
    event_num, event = file.meet.last_event
    entry = event.last_entry

    # Get attribute prefix
    if event_type == ResultType.PRELIM:
        prefix = "prelim"
    elif event_type == ResultType.SWIMOFF:
        prefix = "swimoff"
    elif event_type == ResultType.FINAL:
        prefix = "finals"
    else:
        raise ValueError("Invalid event type!")

    # Set attributes
    setattr(entry, f"{prefix}_time", time)
    setattr(entry, f"{prefix}_course", course)
    setattr(entry, f"{prefix}_time_code", time_code)
    setattr(entry, f"{prefix}_dq_info", dq_info)
    setattr(entry, f"{prefix}_heat", heat)
    setattr(entry, f"{prefix}_lane", lane)
    setattr(entry, f"{prefix}_heat_place", heat_place)
    setattr(entry, f"{prefix}_overall_place", overall_place)
    setattr(entry, f"{prefix}_date", date_)

    event.last_entry = entry
    file.meet.last_event = (event_num, event)

    return file


def f3_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse an F3 relay swimmer list."""
    relay_swimmers: list[Optional[Swimmer]] = [None for _ in range(8)]

    for x in range(8):
        offset = x * 13  # 13 chars per swimmer entry

        swimmer_meet_id = safe_cast(int, extract(line, 4 + offset, 5), default=-1)
        if swimmer_meet_id == -1:
            # Out of swimmers
            break

        swimmer = file.meet.swimmers[swimmer_meet_id]
        swimmer_leg = safe_cast(int, extract(line, 15 + offset, 1))

        # Assume Hytek makes their files correctly
        relay_swimmers[swimmer_leg - 1] = swimmer

    # Get entry
    event_num, event = file.meet.last_event
    entry = event.last_entry

    # Set swimmers
    entry.swimmers = [x for x in relay_swimmers if x]

    # Set the age correctly now
    event.age_min, event.age_max = get_age_group(
        age_min=event.age_min, age_max=event.age_max, swimmer_age=entry.swimmers[0].age
    )

    # Update classes
    event.last_entry = entry
    file.meet.last_event = (event_num, event)
    return file
