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

    SCM = "M", "1", 1
    SCY = "Y", "2", 2
    LCM = "L", "3", 3
    DQ = "X"
    UNKNOWN = "U"
