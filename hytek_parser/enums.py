from typing import Type

from aenum import Enum, MultiValue, Unique


class Gender(Enum):
    """Swimmer gender."""

    _settings_ = Unique

    MALE = "M"
    FEMALE = "F"
    UNKNOWN = "U"


class Stroke(Enum):
    """Types of swimming strokes."""

    _settings_ = Unique

    FREESTYLE = "A"
    BACKSTROKE = "B"
    BREASTSTROKE = "C"
    BUTTERFLY = "D"
    MEDELY = "E"
    UNKNOWN = "U"


class MeetType(Enum):
    """Types of swim meets."""

    _settings_ = Unique, MultiValue

    TIME_TRIALS = "00", "0", 0
    INVITATIONAL = "01", "1", 1
    REGIONAL = "02", "2", 2
    LSC_CHAMPIONSHIP = "03", "3", 3
    ZONE = "04", "4", 4
    ZONE_CHAMPIONSHIP = "05", "5", 5
    NATIONAL_CHAMPIONSHIP = "06", "6", 6
    JUNIORS = "07", "7", 7
    SENIORS = "08", "8", 8
    DUAL = "09", "9", 9
    INTERNATIONAL = "0A", "A"
    OPEN = "0B", "B"
    LEAGUE = "0C", "C"
    UNKNOWN = "UUUUU"


class Course(Enum):
    """Types of swimming courses."""

    _settings_ = Unique, MultiValue

    SCM = "S", "M", "1", 1
    SCY = "Y", "2", 2
    LCM = "L", "3", 3
    # Hytek doesn't put in a course for DFS
    DQ = "X", " ", ""
    UNKNOWN = "U"


class GenderAge(Enum):
    """Age "weighted" gender names."""

    _settings_ = Unique

    MEN_S = "M"
    BOY_S = "B"
    WOMEN_S = "W"
    GIRL_S = "G"
    UNKNOWN = "U"


class ReplacedTimeTimeCode(Enum):
    """Time codes that replace the swimmer's time."""

    _settings_ = Unique

    NO_TIME = "NT"
    NO_SHOW = "NS"
    DID_NOT_FINISH = "DNF"
    DISQUALIFICATION = "DQ"
    SCRATCH = "SCR"
    UNKNOWN = "U"


class WithTimeTimeCode(Enum):
    """Time codes that are listed adjacent to the swimmer's time."""

    _settings_ = Unique, MultiValue

    NORMAL = " ", ""
    UNKNOWN = "U"
    NO_SHOW = "R"
    SCRATCH = "S"

    DISQUALIFICATION = "Q"
    FALSE_START = "F"
    DID_NOT_FINISH = "D"

    @classmethod
    def is_dq_code(cls: Type["WithTimeTimeCode"], x: "WithTimeTimeCode") -> bool:
        """Check if this is a DQ code."""
        return (
            x == cls.DISQUALIFICATION or x == cls.FALSE_START or x == cls.DID_NOT_FINISH
        )


class DisqualificationCode(Enum):
    """USA Swimming disqualification codes."""

    _settings_ = Unique, MultiValue

    # Butterfly
    FLY_KICK_ALTERNATING = "1A"
    FLY_KICK_BREAST = "1B"
    FLY_KICK_SCISSORS = "1C"

    FLY_ARMS_NON_SIMULTANEOUS = "1E"
    FLY_ARMS_UNDERWATER_RECOVERY = "1F"

    FLY_TOUCH_ONE_HAND = "1J"
    FLY_TOUCH_NOT_SEPERATED = "1K"
    FLY_TOUCH_NON_SIMULTANEOUS = "1L"
    FLY_TOUCH_NO_TOUCH = "1M"

    FLY_NOT_TOWARDS_THE_BREAST_OFF_WALL = "1N"
    FLY_HEAD_DID_NOT_BREAK_SURFACE_BY_15M = "1P"
    FLY_RE_SUBMERGED = "1R"

    FLY_OTHER = "1T"

    # Backstroke
    BACK_TURN_NO_TOUCH_AT_TURN = "2A"
    BACK_TURN_DELAY_INITIATING_ARM_PULL = "2B"
    BACK_TURN_DELAY_INITIATING_TURN = "2C"
    BACK_TURN_MULTIPLE_STROKES = "2D"

    BACK_TOES_OVER_LIP_OF_GUTTER_AFTER_START = "2E"
    BACK_HEAD_DID_NOT_BREAK_SURFACE_BY_15M = "2F"

    BACK_RE_SUBMERGED = "2G"
    BACK_NOT_ON_BACK_OFF_WALL = "2H"
    BACK_SHOULDERS_PAST_VERTICAL_TOWARDS_THE_BREAST = "2L"

    BACK_OTHER = "2T"

    # Breaststroke
    BREAST_KICK_ALTERNATING = "3A"
    BREAST_KICK_BUTTERFLY = "3B"
    BREAST_KICK_SCISSORS = "3C"

    BREAST_ARMS_PAST_HIPLINE = "3D"
    BREAST_ARMS_NON_SIMULTANEOUS = "3E"
    BREAST_ARMS_TWO_STROKES_UNDER = "3F"
    BREAST_ARMS_NOT_IN_SAME_HORIZONTAL_PLANE = "3G"
    BREAST_ARMS_ELBOWS_RECOVERED_OVER_WATER = "3H"

    BREAST_TOUCH_ONE_HAND = "3J"
    BREAST_TOUCH_NOT_SEPERATED = "3K"
    BREAST_TOUCH_NON_SIMULTANEOUS = "3L"
    BREAST_TOUCH_NO_TOUCH = "3M"
    BREAST_NOT_TOWARDS_THE_BREAST_OFF_WALL = "3N"

    BREAST_CYCLE_KICK_BEFORE_PULL = "3P"
    BREAST_CYCLE_HEAD_NOT_UP = "3R"
    BREAST_CYCLE_INCOMPLETE = "3S"

    BREAST_OTHER = "3T"

    # Freestyle
    FREE_NO_TOUCH_AT_TURN = "4A"
    FREE_HEAD_DID_NOT_BREAK_SURFACE_BY_15M = "4B"
    FREE_RE_SUBMERGED = "4V"
    FREE_OTHER = "4T"

    # Individual Medley
    IM_STROKE_INFRACTION = "5A"
    IM_OUT_OF_SEQUENCE = "5B"
    IM_OTHER = "5T"

    # Relays
    RELAY_STROKE_INFRACTION_SWIMMER_1 = "6A"
    RELAY_STROKE_INFRACTION_SWIMMER_2 = "6B"
    RELAY_STROKE_INFRACTION_SWIMMER_3 = "6C"
    RELAY_STROKE_INFRACTION_SWIMMER_4 = "6D"

    RELAY_EARLY_TAKE_OFF_SWIMMER_2 = "6F"
    RELAY_EARLY_TAKE_OFF_SWIMMER_3 = "6G"
    RELAY_EARLY_TAKE_OFF_SWIMMER_4 = "6H"

    RELAY_CHANGED_ORDER = "6L"
    RELAY_OTHER = "6T"

    # Miscellaneous
    MISC_FALSE_START = "7A"
    MISC_DECLARED_FALSE_START = "7B"

    MISC_DID_NOT_FINISH = "7C"
    MISC_DELAY_OF_MEET = "7D"

    MISC_ENTERED_WATER_WITHOUT_PERMISSION = "7F"
    MISC_INTERFERED_WITH_ANOTHER_SWIMMER = "7G"

    MISC_WALKING_ON_BOTTOM = "7H"
    MISC_STANDING_ON_BOTTOM = "7J"

    MISC_PULLING_ON_LANE_LINE = "7K"
    MISC_FINISHED_IN_WRONG_LANE = "7L"

    MISC_UNSPORTSMANLIKE_CONDUCT = "7M"
    MISC_NO_SHOW_PENALTY = "7N"

    MISC_OTHER = "7T"

    # Defaults
    UNKNOWN = "UU"


class ResultType(Enum):
    """Event types."""

    _settings_ = Unique

    PRELIM = "P"
    FINAL = "F"
    SWIMOFF = "S"
    UNKNOWN = "U"
