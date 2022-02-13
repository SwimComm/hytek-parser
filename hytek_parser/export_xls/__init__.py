"""Header lists for the `csv.DictReader` when reading Hytek-produced CSVs."""
import xlrd

from hytek_parser._utils import safe_cast
from hytek_parser.types import StrOrBytesPath

from ._utils import (
    ExportXlsParseError,
    extract_plain_value,
    extract_time_value,
    get_first_row_index,
    get_offsets_from_header,
)
from .schemas import EventResultEntry, ParsedEventResultXlsFile

__all__ = ["ExportXlsParseError", "parse_event_export_xls"]

_ALL_PARSING_ELEMENTS = [
    "name",
    "age",
    "team",
    "seed time",
    "prelim time",
    "finals time",
]


def parse_event_export_xls(
    file: StrOrBytesPath, parsing_elements: list[str] = _ALL_PARSING_ELEMENTS
) -> ParsedEventResultXlsFile:
    """Parse a Hytek MeetManager .hy3 file.

    Args:
        file (StrOrBytesPath): A path to the file to parse.
        parsing_elements (Sequence[str]): Elements to extract from the file.
            Valid elements: 'name', 'age', 'team', 'seed time',
                            'prelim time', 'finals time'

    Returns:
        ParsedEventHyvFile: The parsed file.
    """
    book = xlrd.open_workbook(file)
    sheet = book.sheet_by_index(0)

    # Get event name
    event_name = str(sheet.cell_value(1, 0))

    # Extract the header row
    # This should be one with "Name" as it's first element
    for rx in range(sheet.nrows):
        row = sheet.row(rx)
        if str(row[0].value).lower() == "name":
            header_row = [str(e.value).lower() for e in row]
            header_row_index = rx
            break

    # Make sure we have a header row
    if header_row is None:
        raise ExportXlsParseError("Could not find header row.")

    first_row_index = get_first_row_index(sheet, header_row_index)

    # Only parse times in the header row
    if "seed time" in parsing_elements and "seed time" not in header_row:
        parsing_elements.pop(parsing_elements.index("seed time"))
    if "prelim time" in parsing_elements and "prelim time" not in header_row:
        parsing_elements.pop(parsing_elements.index("prelim time"))
    if "finals time" in parsing_elements and "finals time" not in header_row:
        parsing_elements.pop(parsing_elements.index("finals time"))

    # Determine offsets to extract from
    offsets = get_offsets_from_header(
        sheet, header_row, first_row_index, parsing_elements
    )

    # Start parsing rows
    results = []
    rx = first_row_index
    while rx < sheet.nrows and sheet.cell_value(rx, 0).strip() != "":
        row = sheet.row(rx)

        place = safe_cast(int, row[0].value, -1)

        if place == -1 and row[0].value != "---":
            rx += 1
            continue

        name = extract_plain_value("name", row, offsets)
        age = extract_plain_value("age", row, offsets, cast_to=int)
        team = extract_plain_value("team", row, offsets)

        seed_time, seed_time_extra, seed_time_qualifications = extract_time_value(
            "seed time", row, offsets
        )
        prelim_time, prelim_time_extra, prelim_time_qualifications = extract_time_value(
            "prelim time", row, offsets
        )
        finals_time, finals_time_extra, finals_time_qualifications = extract_time_value(
            "finals time", row, offsets
        )

        results.append(
            EventResultEntry(
                place=place,
                swimmer_name=name,
                swimmer_age=age,
                swimmer_team=team,
                seed_time=seed_time,
                seed_time_extra=seed_time_extra,
                seed_time_qualifications=seed_time_qualifications,
                prelim_time=prelim_time,
                prelim_time_extra=prelim_time_extra,
                prelim_time_qualifications=prelim_time_qualifications,
                finals_time=finals_time,
                finals_time_extra=finals_time_extra,
                finals_time_qualifications=finals_time_qualifications,
            )
        )

        rx += 1

    return ParsedEventResultXlsFile(
        event_name=event_name, parsing_elements=tuple(parsing_elements), results=results
    )
