import datetime
import unittest

from tiny_utc_offset import parse_utc_offset, ParseError


class TestParseUtcOffset(unittest.TestCase):
    def test_z_is_utc(self):
        tz = parse_utc_offset("Z")
        self.assertIs(tz, datetime.timezone.utc)

    def test_bare_utc_keyword(self):
        tz = parse_utc_offset("UTC")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(0))

    def test_bare_gmt_keyword(self):
        tz = parse_utc_offset("GMT")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(0))

    def test_case_insensitive_keyword(self):
        tz = parse_utc_offset("utc")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(0))

    def test_utc_prefix_with_colon(self):
        tz = parse_utc_offset("UTC+02:00")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=2))

    def test_gmt_prefix_no_colon(self):
        tz = parse_utc_offset("GMT-5")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=-5))

    def test_signed_hhmm_no_colon(self):
        tz = parse_utc_offset("+0530")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=5, minutes=30))

    def test_signed_negative_hhmm_no_colon(self):
        tz = parse_utc_offset("-0530")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=-5, minutes=-30))

    def test_signed_hh_colon_mm(self):
        tz = parse_utc_offset("+05:30")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=5, minutes=30))

    def test_signed_negative_hh_colon_mm(self):
        tz = parse_utc_offset("-09:00")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=-9))

    def test_signed_hours_only(self):
        tz = parse_utc_offset("+05")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=5))

    def test_signed_single_digit_hour(self):
        tz = parse_utc_offset("-5")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=-5))

    def test_whitespace_trimmed(self):
        tz = parse_utc_offset("  +03:00  ")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=3))

    def test_trailing_z_ignored(self):
        tz = parse_utc_offset("+0530Z")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(hours=5, minutes=30))

    def test_negative_zero_offset(self):
        tz = parse_utc_offset("-00:00")
        self.assertEqual(tz.utcoffset(None), datetime.timedelta(0))

    def test_offset_name_preserved(self):
        tz = parse_utc_offset("+02:00")
        self.assertEqual(tz.tzname(None), "+02:00")

    def test_minute_out_of_range_raises(self):
        with self.assertRaises(ParseError):
            parse_utc_offset("+05:75")

    def test_empty_string_raises(self):
        with self.assertRaises(ParseError):
            parse_utc_offset("")

    def test_garbage_raises(self):
        with self.assertRaises(ParseError):
            parse_utc_offset("hello")

    def test_non_string_raises(self):
        with self.assertRaises(ParseError):
            parse_utc_offset(5)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
