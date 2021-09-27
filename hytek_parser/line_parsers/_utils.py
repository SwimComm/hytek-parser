from collections import defaultdict

_MEET_TYPES: dict[str, str] = {
    "00": "Time Trials",
    "01": "Invitational",
    "02": "Regional",
    "03": "LSC Championship",
    "04": "Zone",
    "05": "Zone Championship",
    "06": "National Championship",
    "07": "Juniors",
    "08": "Seniors",
    "09": "Dual",
    "0A": "International",
    "0B": "Open",
    "0C": "League",
}
MEET_TYPES: defaultdict[str, str] = defaultdict(lambda: "Unknown", _MEET_TYPES)

_MEET_COURSES: dict[str, str] = {
    # SCM
    "1": "SCM",
    "M": "SCM",
    # SCY
    "2": "SCY",
    "Y": "SCY",
    # LCM
    "3": "LCM",
    "L": "LCM",
    # Other
    "X": "Disqualified",
}
MEET_COURSES: defaultdict[str, str] = defaultdict(lambda: "Unknown", _MEET_COURSES)


def extract(string: str, start: int, len_: int) -> str:
    """Extract a section of a certain length from a string.

    Args:
        string (str): The string to extract from.
        start (int): How many chars to move forward.
        len_ (int): The amount of chars to extract.

    Returns:
        str: The extracted string.
    """
    start -= 1
    return string[start : start + len_].rstrip()
