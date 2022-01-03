from typing import Any

from ...enums import DisqualificationCode
from ...schemas import ParsedHytekFile
from .._utils import extract, select_from_enum


def h1_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse a G1 split time entry."""
    # Get event
    event_num, event = file.meet.last_event
    entry = event.last_entry

    # Get dq code and message
    dq_code = select_from_enum(DisqualificationCode, extract(line, 3, 2))
    dq_info = extract(line, 5, 124)  # Whitespace is stripped

    assert (
        entry.prelim_dq_info or entry.swimoff_dq_info or entry.finals_dq_info
    ), "There must be a DQ for there to be an H1 line"

    if entry.finals_dq_info:
        # DQ happened in prelims
        assert (
            entry.finals_dq_info.code == dq_code
        ), "DQ Codes should match in the H1 line"

        entry.finals_dq_info.info_str = dq_info
    elif entry.swimoff_dq_info:
        # DQ happened in prelims
        assert (
            entry.swimoff_dq_info.code == dq_code
        ), "DQ Codes should match in the H1 line"

        entry.swimoff_dq_info.info_str = dq_info
    elif entry.prelim_dq_info:
        # DQ happened in prelims
        assert (
            entry.prelim_dq_info.code == dq_code
        ), "DQ Codes should match in the H1 line"

        entry.prelim_dq_info.info_str = dq_info

    event.last_entry = entry
    file.meet.last_event = (event_num, event)

    return file
