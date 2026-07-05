import unittest

from hytek_parser.hy3.schemas import (
    ParsedHytekFile, Meet, Team, DisqualificationInfo,
)
from hytek_parser.hy3.enums import DisqualificationCode
from hytek_parser.hy3.line_parsers.d_swimmer_parsers import d1_parser
from hytek_parser.hy3.line_parsers.e_event_parsers import e1_parser


class TestH2DqParser(unittest.TestCase):

    def _file_with_entry(self):
        opts = {"default_country": "USA"}
        file = ParsedHytekFile()
        file.meet = Meet()
        file.meet.last_team = ("FOO", Team("Foo Bar", "FOO", "foo", "", "", "", "", "", "", "", "", "", "", "", {}))
        d_line = "D1M   27Hansen              Mads                                                        10272010 13                             27"
        e_line = "E1M   27HanseXX    50D 11109  0U  0.00 22X   37.41S   37.41S    0.00    0.00  0NN               N                               70"
        file = d1_parser(d_line, file, opts)
        file = e1_parser(e_line, file, opts)
        return file, opts

    def test_h2_sets_detail_on_finals_dq(self) -> None:
        from hytek_parser.hy3.line_parsers.h_dq_parsers import h2_parser
        file, opts = self._file_with_entry()
        entry = file.meet.last_event[1].last_entry
        entry.finals_dq_info = DisqualificationInfo(DisqualificationCode.FLY_KICK_ALTERNATING, "Stroke Infraction swimmer #1")
        result = h2_parser("H21AAlternating Kick - fly", file, opts)
        self.assertEqual("Alternating Kick - fly", result.meet.last_event[1].last_entry.finals_dq_info.info_str_detail)

    def test_h2_no_dq_is_noop(self) -> None:
        from hytek_parser.hy3.line_parsers.h_dq_parsers import h2_parser
        file, opts = self._file_with_entry()
        # No dq_info set on any slot → parser must not raise, just return file.
        result = h2_parser("H21AAlternating Kick - fly", file, opts)
        entry = result.meet.last_event[1].last_entry
        self.assertIsNone(entry.finals_dq_info)

    def test_h2_sets_detail_on_swimoff_dq(self) -> None:
        from hytek_parser.hy3.line_parsers.h_dq_parsers import h2_parser
        file, opts = self._file_with_entry()
        entry = file.meet.last_event[1].last_entry
        entry.swimoff_dq_info = DisqualificationInfo(DisqualificationCode.FLY_KICK_ALTERNATING, "Stroke Infraction swimmer #1")
        result = h2_parser("H21AAlternating Kick - fly", file, opts)
        entry = result.meet.last_event[1].last_entry
        self.assertEqual("Alternating Kick - fly", entry.swimoff_dq_info.info_str_detail)
        self.assertIsNone(entry.finals_dq_info)

    def test_h2_sets_detail_on_prelim_dq(self) -> None:
        from hytek_parser.hy3.line_parsers.h_dq_parsers import h2_parser
        file, opts = self._file_with_entry()
        entry = file.meet.last_event[1].last_entry
        entry.prelim_dq_info = DisqualificationInfo(DisqualificationCode.FLY_KICK_ALTERNATING, "Stroke Infraction swimmer #1")
        result = h2_parser("H21AAlternating Kick - fly", file, opts)
        entry = result.meet.last_event[1].last_entry
        self.assertEqual("Alternating Kick - fly", entry.prelim_dq_info.info_str_detail)
        self.assertIsNone(entry.finals_dq_info)
        self.assertIsNone(entry.swimoff_dq_info)

    def test_h2_empty_detail_is_none(self) -> None:
        from hytek_parser.hy3.line_parsers.h_dq_parsers import h2_parser
        file, opts = self._file_with_entry()
        entry = file.meet.last_event[1].last_entry
        entry.finals_dq_info = DisqualificationInfo(DisqualificationCode.FLY_KICK_ALTERNATING, "Stroke Infraction swimmer #1")
        line = "H21A" + " " * 126  # detail region (cols 5+) is blank
        result = h2_parser(line, file, opts)
        entry = result.meet.last_event[1].last_entry
        self.assertIsNone(entry.finals_dq_info.info_str_detail)


if __name__ == "__main__":
    unittest.main()
