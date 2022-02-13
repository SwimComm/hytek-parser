"""A parsing dict and partial csv.DictReader for Event HYV exports."""
import csv
from datetime import datetime
from functools import partial

from hytek_parser._utils import safe_cast, select_from_enum
from hytek_parser.hy3.enums import Course, Gender, Stroke
from hytek_parser.hyv.enums import ChampionshipEventType, SwimmersEventType
from hytek_parser.hyv.schemas import EventExport, ParsedEventHyvFile
from hytek_parser.types import DictReader, StrOrBytesPath

__all__ = ["EVENT_HYV_CSV_HEADER", "EventHyvReader", "parse_event_hyv"]

EVENT_HYV_CSV_HEADER = [
    "event_no",
    "event_championship_type",
    "event_gender",
    "event_swimmers_type",
    "event_min_age",
    "event_max_age",
    "event_distance",
    "event_stroke",
    "unknown1",
    "unknown2_time",
    "unknown3",
    "unknown4",
    "unknown5",
    "unknown6_time",
    "unknown7",
    "unknown8_time",
    "unknown9",
    "unknown10",
]

EventHyvReader = partial(DictReader, fieldnames=EVENT_HYV_CSV_HEADER, delimiter=";")


def parse_event_hyv(file: StrOrBytesPath) -> ParsedEventHyvFile:
    """Parse a Hytek MeetManager .hyv event export file.

    Args:
        file (StrOrBytesPath): A path to the file to parse.

    Returns:
        ParsedEventHyvFile: The parsed file.
    """
    with open(file, "r") as f:
        first_line_reader = csv.reader(f, delimiter=";")
        (
            name,
            raw_start_date,
            raw_end_date,
            raw_date_other,
            raw_course,
            pool,
            unknown_space,
            software_vendor,
            software_version,
            unknown_code,
            unknown_id,
        ) = next(first_line_reader)

        events: list[EventExport] = []
        reader = EventHyvReader(f)
        for line in reader:
            events.append(
                EventExport(
                    number=safe_cast(int, line["event_no"]),
                    championship_type=select_from_enum(
                        ChampionshipEventType, line["event_championship_type"]
                    ),
                    gender=select_from_enum(Gender, line["event_gender"]),
                    swimmer_type=select_from_enum(
                        SwimmersEventType, line["event_swimmers_type"]
                    ),
                    min_age=safe_cast(int, line["event_min_age"]),
                    max_age=safe_cast(int, line["event_max_age"]),
                    distance=safe_cast(int, line["event_distance"]),
                    stroke=select_from_enum(Stroke, line["event_stroke"]),
                    unknown1=line["unknown1"],
                    unknown2_time=line["unknown2_time"],
                    unknown3=line["unknown3"],
                    unknown4=line["unknown4"],
                    unknown5=line["unknown5"],
                    unknown6_time=line["unknown6_time"],
                    unknown7=line["unknown7"],
                    unknown8_time=line["unknown8_time"],
                    unknown9=line["unknown9"],
                    unknown10=line["unknown10"],
                )
            )

        return ParsedEventHyvFile(
            meet_name=name,
            meet_course=select_from_enum(Course, raw_course),
            meet_pool=pool,
            meet_start_date=datetime.strptime(raw_start_date, "%m/%d/%Y").date(),
            meet_end_date=datetime.strptime(raw_end_date, "%m/%d/%Y").date(),
            meet_date_other=datetime.strptime(raw_date_other, "%m/%d/%Y").date(),
            file_software_vendor=software_vendor,
            file_software_version=software_version,
            file_unknown_space_7=unknown_space,
            file_unknown_code=unknown_code,
            file_unknown_id=unknown_id,
            events=events,
        )
