from typing import Any, Callable

from ...schemas import ParsedHytekFile
from .a_file_parsers import a1_parser
from .b_meet_parsers import b1_parser, b2_parser
from .c_team_parsers import c1_parser, c2_parser, c3_parser
from .d_swimmer_parsers import d1_parser
from .e_event_parsers import e1_parser, e2_parser
from .f_relay_parsers import f1_parser, f2_parser, f3_parser
from .g_split_parsers import g1_parser
from .h_dq_parsers import h1_parser

LINE_PARSERS: dict[
    str, Callable[[str, ParsedHytekFile, dict[str, Any]], ParsedHytekFile]
] = {
    # File info
    "A1": a1_parser,
    # Meet info
    "B1": b1_parser,
    "B2": b2_parser,
    # Team info
    "C1": c1_parser,
    "C2": c2_parser,
    "C3": c3_parser,
    # Swimmer info
    "D1": d1_parser,
    # Event info
    "E1": e1_parser,
    "E2": e2_parser,
    # Relay info
    "F1": f1_parser,
    "F2": f2_parser,
    "F3": f3_parser,
    # Splits
    "G1": g1_parser,
    # DQ info
    "H1": h1_parser,
}
