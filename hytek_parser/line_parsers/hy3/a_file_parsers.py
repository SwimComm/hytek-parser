from datetime import datetime
from typing import Any

from ...schemas import ParsedHytekFile, Software
from .._utils import extract


def a1_parser(
    line: str, file: ParsedHytekFile, opts: dict[str, Any]
) -> ParsedHytekFile:
    """Parse an A1 line with file info."""
    file.file_description = extract(line, 5, 25)
    file.software = Software(extract(line, 30, 15), extract(line, 45, 10))

    # Add in a 0 to make the datetime library happy
    raw_date = extract(line, 59, 17)
    if raw_date[9] == " ":
        raw_date = raw_date[:9] + "0" + raw_date[10:]

    file.date_created = datetime.strptime(raw_date, "%d%m%Y %I:%M %p")
    file.licensee = extract(line, 76, 53)

    return file
