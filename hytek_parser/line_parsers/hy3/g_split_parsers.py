from typing import Any

from ...enums import ResultType
from ...schemas import ParsedHytekFile
from .._utils import extract, safe_cast, select_from_enum


def g1_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a G1 split time entry."""
    event_type = select_from_enum(ResultType, extract(line, 3, 1))

    # Get event
    event_num, event = file.meet.last_event
    entry = event.last_entry

    # Read splits
    line_pos = 4
    splits: dict[int, float] = {}
    while line_pos < 124 and line[line_pos] != " ":
        split_num = safe_cast(int, extract(line, line_pos, 2))
        split_time = safe_cast(float, extract(line, line_pos + 2, 8))

        splits[split_num] = split_time
        line_pos += 11  # MM for some reason specifies P/S/F every time???

    # Set correct attribute
    if event_type == ResultType.PRELIM:
        entry.prelim_splits |= splits
    elif event_type == ResultType.SWIMOFF:
        entry.swimoff_splits |= splits
    elif event_type == ResultType.FINAL:
        entry.finals_splits |= splits
    else:
        raise ValueError("Invalid event type!")

    event.last_entry = entry
    file.meet.last_event = (event_num, event)

    return file
