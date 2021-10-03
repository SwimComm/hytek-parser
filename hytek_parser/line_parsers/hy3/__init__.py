from typing import Any, Callable

from ...schemas import ParsedHytekFile
from .a_file_parsers import a1_parser
from .b_meet_parsers import b1_parser, b2_parser
from .c_team_parsers import c1_parser, c2_parser

LINE_PARSERS: dict[
    str, Callable[[str, ParsedHytekFile, dict[str, Any]], ParsedHytekFile]
] = {
    "A1": a1_parser,
    "B1": b1_parser,
    "B2": b2_parser,
    "C1": c1_parser,
    "C2": c2_parser,
}
