from datetime import datetime
from typing import Any

from hytek_parser._utils import extract, get_age_group, safe_cast, select_from_enum
from hytek_parser.hy3._utils import parse_time, parse_time_or_none
from hytek_parser.hy3.enums import (
    Course,
    DisqualificationCode,
    GenderAge,
    ResultType,
    Stroke,
    WithTimeTimeCode,
)
from hytek_parser.hy3.schemas import (
    DisqualificationInfo,
    Gender,
    ParsedHytekFile,
    Swimmer,
)


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
    event_number = extract(line, 39, 4)
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
    )

    # Will populate this later
    entry_swimmers: dict[int, Swimmer] = {}

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
        relay_team_id=relay_team,
        relay_swim_team_code=team_code,
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

    # previously-dropped F2 timing fields. The five timing-column
    # offsets are IDENTICAL to e2_parser; only alt_time_code differs because F2
    # has a 15-column gap before its date field (date at col 103, not 88).
    # F2 alt_time_code lives at col 111, not col 96.
    pad_time      = parse_time_or_none(extract(line, 63, 12))
    button_1_time = parse_time_or_none(extract(line, 39, 8))
    button_2_time = parse_time_or_none(extract(line, 47, 8))
    button_3_time = parse_time_or_none(extract(line, 55, 8))
    backup_4_time = parse_time_or_none(extract(line, 75, 8))
    alt_time_code = extract(line, 111, 1) or None  # F2 offset; observed: 'A'/'K'/blank

    raw_date = extract(line, 103, 8).strip()
    date_ = datetime.strptime(raw_date, "%m%d%Y").date() if raw_date else None

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
    setattr(entry, f"{prefix}_pad_time", pad_time)
    setattr(entry, f"{prefix}_button_1_time", button_1_time)
    setattr(entry, f"{prefix}_button_2_time", button_2_time)
    setattr(entry, f"{prefix}_button_3_time", button_3_time)
    setattr(entry, f"{prefix}_backup_4_time", backup_4_time)
    setattr(entry, f"{prefix}_alt_time_code", alt_time_code)

    event.last_entry = entry
    file.meet.last_event = (event_num, event)

    return file


def f3_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse an F3 relay swimmer list."""
    relay_swimmers: dict[int, Swimmer] = {}

    for x in range(8):
        offset = x * 13  # 13 chars per swimmer entry

        swimmer_meet_id = safe_cast(int, extract(line, 4 + offset, 5), default=-1)
        if swimmer_meet_id == -1:
            # Out of swimmers
            break

        swimmer = file.meet.swimmers[swimmer_meet_id]
        swimmer_leg = safe_cast(int, extract(line, 15 + offset, 1))

        # Hy-Tek encodes legs 1..8; preserve the leg number as-is.
        relay_swimmers[swimmer_leg] = swimmer

    # Get entry
    event_num, event = file.meet.last_event
    entry = event.last_entry

    # Set swimmers (leg-keyed)
    entry.swimmers = relay_swimmers

    # Set the age correctly now using the lowest-numbered leg's swimmer.
    # Using min(keys()) instead of entry.swimmers[1] handles the edge case
    # where leg 1 is absent (e.g., scratched before F3 was emitted, or a
    # malformed F3 line). The if-guard handles the empty-dict case where
    # F3 was emitted with no parseable swimmers at all.
    if entry.swimmers:
        first_leg_swimmer = entry.swimmers[min(entry.swimmers.keys())]
        event.age_min, event.age_max = get_age_group(
            age_min=event.age_min,
            age_max=event.age_max,
            swimmer_age=first_leg_swimmer.age,
        )

    # Update classes
    event.last_entry = entry
    file.meet.last_event = (event_num, event)
    return file
