from typing import Any

from hytek_parser._utils import extract, select_from_enum
from hytek_parser.hy3.enums import DisqualificationCode
from hytek_parser.hy3.schemas import ParsedHytekFile


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


def h2_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse an H2 line: the specific, human-readable DQ infraction detail.

    Attaches the detail text to whichever DQ slot the preceding H1 populated
    (finals -> swimoff -> prelim), mirroring h1_parser's resolution. Unlike H1,
    the H2 2-char code is NOT asserted against the DQ code (it is a stroke/leg
    sub-classification, not the same DisqualificationCode). No-op if no DQ slot
    is set.
    """
    event_num, event = file.meet.last_event
    entry = event.last_entry

    detail = extract(line, 5, 124) or None

    if entry.finals_dq_info:
        entry.finals_dq_info.info_str_detail = detail
    elif entry.swimoff_dq_info:
        entry.swimoff_dq_info.info_str_detail = detail
    elif entry.prelim_dq_info:
        entry.prelim_dq_info.info_str_detail = detail

    event.last_entry = entry
    file.meet.last_event = (event_num, event)
    return file
