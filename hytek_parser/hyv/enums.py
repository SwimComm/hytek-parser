from aenum import Enum, Unique


class ChampionshipEventType(Enum):
    """Championship event types: prelim, final, swimoff, time trial."""

    _settings_ = Unique

    PRELIM_FINALS = "P"
    TIMED_FINALS = "F"
    SWIMOFF = "S"
    TIME_TRIAL = "X"  # ? It may be something else, but I believe time trials are X

    UNKNOWN = "U"


class SwimmersEventType(Enum):
    """Swimmer's event type: Relay or Individual."""

    _settings_ = Unique

    INDIVIDUAL = "I"
    RELAY = "R"

    UNKNOWN = "U"
