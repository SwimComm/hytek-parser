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
    NO_SHOW = "R"
    DISQUALIFICATION = "Q"
    FALSE_START = "F"
    SCRATCH = "S"
    UNKNOWN = "U"


class DisqualificationCode(Enum):
    """USA Swimming disqualification codes."""

    _settings_ = Unique

    # Butterfly
    FLY_KICK_ALTERNATING = "1A"
    FLY_KICK_BREAST = "1B"
    FLY_KICK_SCISSORS = "1C"

    FLY_ARMS_NON_SIMULTANEOUS = "1E"
    FLY_ARMS_UNDERWATER_RECOVERY = "1F"

    FLY_TOUCH_ONE_HAND = "1J"
    FLY_TOUCH_NO_TOUCH = "1K"
    FLY_TOUCH_NON_SIMULTANEOUS = "1L"

    FLY_NOT_TOWARDS_THE_BREAST_OFF_WALL = "1M"
    FLY_HEAD_DID_NOT_BREAK_SURFACE_BY_15M = "1N"

    # Backstroke
    BACK_NO_TOUCH_AT_TURN = "2I"
    BACK_NON_CONTINUOUS_TURNING_ACTION = "2J"
    BACK_NOT_ON_BACK_OFF_WALL = "2K"

    BACK_SHOULDERS_PAST_VERTICAL_TOWARDS_THE_BREAST = "2L"
    BACK_HEAD_DID_NOT_BREAK_SURFACE_BY_15M = "2N"
    BACK_TOES_OVER_LIP_OF_GUTTER_AFTER_START = "2P"

    BACK_DID_NOT_FINISH_ON_BACK = "2Q"
    BACK_RE_SUBMERGED = "2R"

    BACK_PAST_VERTICAL_AT_TURN_DELAY_INITIATING_ARM_PULL = "2S"
    BACK_PAST_VERTICAL_AT_TURN_DELAY_INITIATING_TURN = "2T"
    BACK_PAST_VERTICAL_AT_TURN_MULTIPLE_STROKES = "2U"

    # Breaststroke
    BREAST_KICK_ALTERNATING = "3A"
    BREAST_KICK_NON_SIMULTANEOUS = "3B"
    BREAST_KICK_BUTTERFLY = "3C"
    BREAST_KICK_SCISSORS = "3D"

    BREAST_ARMS_PAST_HIPLINE = "3E"
    BREAST_ARMS_NON_SIMULTANEOUS = "3F"
    BREAST_ARMS_TWO_STROKES_UNDER = "3G"
    BREAST_ARMS_NOT_IN_SAME_HORIZONTAL_PLANE = "3H"
    BREAST_ARMS_ELBOWS_RECOVERED_OVER_WATER = "3I"

    BREAST_TOUCH_ONE_HAND = "3J"
    BREAST_TOUCH_NO_TOUCH = "3K"
    BREAST_TOUCH_NON_SIMULTANEOUS = "3L"
    BREAST_NOT_TOWARDS_THE_BREAST_OFF_WALL = "3M"

    BREAST_CYCLE_HEAD_NOT_UP = "3P"
    BREAST_CYCLE_INCOMPLETE = "3Q"

    # Freestyle
    FREE_NO_TOUCH_AT_TURN = "4K"
    FREE_HEAD_DID_NOT_BREAK_SURFACE_BY_15M = "4N"

    # Individual Medley
    IM_OUT_OF_SEQUENCE = "5P"

    # Relays
    RELAY_STROKE_INFRACTION_1 = "61"
    RELAY_STROKE_INFRACTION_2 = "62"
    RELAY_STROKE_INFRACTION_3 = "63"
    RELAY_STROKE_INFRACTION_4 = "64"

    RELAY_EARLY_TAKE_OFF_SWIMMER_2 = "66"
    RELAY_EARLY_TAKE_OFF_SWIMMER_3 = "67"
    RELAY_EARLY_TAKE_OFF_SWIMMER_4 = "68"

    RELAY_CHANGED_ORDER = "6P"
    RELAY_NOT_ENOUGH_SWIMMERS = "6Q"

    # Miscellaneous
    MISC_FALSE_START = "7O"
    MISC_DECLARED_FALSE_START = "7P"

    MISC_DID_NOT_FINISH = "7Q"
    MISC_DELAY_OF_MEET = "7R"

    MISC_ENTERED_WATER_WITHOUT_PERMISSION = "7S"
    MISC_INTERFERED_WITH_ANOTHER_SWIMMER = "7T"

    MISC_WALKING_ON_BOTTOM = "7U"
    MISC_STANDING_ON_BOTTOM = "7V"

    MISC_PULLING_ON_LANE_LINE = "7W"
    MISC_FINISHED_IN_WRONG_LANE = "7X"

    MISC_UNSPORTSMANLIKE_CONDUCT = "7Y"

    MISC_NO_SHOW_PENALTY = "7Z"

    # Defaults
    UNKNOWN = "UU"


class ResultType(Enum):
    """Event types."""

    _settings_ = Unique

    PRELIM = "P"
    FINAL = "F"
    SWIMOFF = "S"
    UNKNOWN = "U"
