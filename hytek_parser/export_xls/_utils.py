from typing import Any, Optional, Type, TypeVar

from hytek_parser._utils import safe_cast


class ExportXlsParseError(Exception):
    """Raised when there is an error parsing an XLS event result export."""

    pass


def get_first_row_index(sheet: Any, header_row_index: int) -> int:
    """Check if the sheet is a a/b/prelims export.

    HEADER
    A-final
    1
    2
    3
    B-final
    4
    5
    6
    Prelims
    7
    ...
    """
    if "final" in sheet.cell_value(header_row_index + 1, 0).lower():
        return header_row_index + 2
    else:
        return header_row_index + 1


def get_offsets_from_header(
    sheet: Any, header_row: list[str], first_row_index: int, parsing_elements: list[str]
) -> dict[str, int]:
    """Determine offsets of data from the header row."""
    # Determine offsets to extract from
    # Currently only extracts name, age, team, seed time, and finals time
    #
    # Yes this loop is inefficient but it works
    offsets = {}
    for elem in parsing_elements:
        offset = 0
        for cell in header_row:
            if cell == elem:
                # Found
                break
            else:
                if "time" in cell:
                    # Times take up three cells
                    offset += 3
                else:
                    # Only one cell
                    offset += 1

        if offset >= len(sheet.row(first_row_index)):
            # Overran the length
            raise ExportXlsParseError(
                f"Invalid header row: {header_row}, "
                + f'offset {offset} out of range for "{elem}".'
            )

        # Set offset
        offsets[elem] = offset + 1  # Starts one over

    return offsets


CastType = TypeVar("CastType")


def extract_plain_value(
    name: str,
    row: list,
    offsets: dict[str, int],
    cast_to: Type[CastType] = str,  # type: ignore[assignment]
    default: CastType = None,
) -> Optional[CastType]:
    """Extract a plain (1 column) value from a row."""
    if name in offsets:
        return safe_cast(cast_to, row[offsets[name]].value, default=default)
    return None


def extract_time_value(
    name: str, row: list, offsets: dict[str, int]
) -> tuple[Optional[float], Optional[str], Optional[str]]:
    """Extract a time (3 column) value from a row."""
    time = time_extra = time_qualifications = None
    if name in offsets:
        offset = offsets[name]

        try:
            minutes, seconds = str(row[offset].value).split(":")
            time = safe_cast(int, minutes) * 60 + safe_cast(float, seconds)
        except ValueError:
            # Not able to unpack values
            time = safe_cast(float, str(row[offset].value), -1)
        time_extra = str(row[offset + 1].value)
        time_qualifications = str(row[offset + 2].value)

    return time, time_extra, time_qualifications
