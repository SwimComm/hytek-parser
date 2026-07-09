import unittest
from hytek_parser.hy3.schemas import EventEntry
from hytek_parser.hy3.enums import Course


class TestEventEntryNewTimingFields(unittest.TestCase):
    """EventEntry gains 19 new attributes (18 timing × 3 prefixes
    + 1 entry-level meet_division)."""

    def _make_entry(self):
        return EventEntry(
            swimmers={},
            relay=False,
            event_number="22X",
            seed_time=0.0,
            seed_course=Course.SCY,
            converted_seed_time=0.0,
            converted_seed_time_course=Course.SCY,
        )

    def test_all_18_timing_fields_default_to_none(self):
        entry = self._make_entry()
        for prefix in ("prelim", "swimoff", "finals"):
            for field in (
                "pad_time", "button_1_time", "button_2_time",
                "button_3_time", "backup_4_time", "alt_time_code",
            ):
                attr = f"{prefix}_{field}"
                self.assertTrue(
                    hasattr(entry, attr),
                    f"EventEntry missing attr {attr}",
                )
                self.assertIsNone(
                    getattr(entry, attr),
                    f"{attr} should default to None",
                )

    def test_meet_division_defaults_to_none(self):
        entry = self._make_entry()
        self.assertTrue(hasattr(entry, "meet_division"))
        self.assertIsNone(entry.meet_division)
        self.assertFalse(entry.exhibition, "exhibition should default to False")


if __name__ == "__main__":
    unittest.main()
