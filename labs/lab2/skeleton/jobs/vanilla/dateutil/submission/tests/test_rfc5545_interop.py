# -*- coding: utf-8 -*-
"""
Tests for RFC 5545 timezone interoperability extensions to the rrule module:

- RDATE TZID / VALUE=DATE / VALUE=DATE-TIME parameter support
- rrulestr tzids parameter, VCALENDAR auto-detection, VTIMEZONE parsing,
  line unfolding, first-VEVENT-only semantics, inline VTIMEZONE priority
- rrule timezone-aware __str__ (TZID / Z suffix), round-tripping
- rrule __eq__ / __hash__ / __repr__ / property accessors / count()
- rrule.to_ical()
- rruleset component accessors, __str__, __eq__, __repr__, copy,
  union, subtract, to_ical, from_str
- "date property specifies multiple timezones" error message
"""
import datetime as _dt_module
from datetime import datetime, timedelta
import unittest

from dateutil import tz
from dateutil.rrule import (
    rrule, rruleset, rrulestr,
    YEARLY, MONTHLY, WEEKLY, DAILY,
    HOURLY, MINUTELY, SECONDLY,
)


NYC = tz.gettz('America/New_York')
BXL = tz.gettz('Europe/Brussels')


class RRuleStrTzidsTest(unittest.TestCase):
    def testRdateWithTZID(self):
        rr = rrulestr("DTSTART:19970902T090000\n"
                      "RDATE;TZID=America/New_York:19970902T090000\n"
                      "RDATE;TZID=America/New_York:19970904T090000\n")
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0, tzinfo=NYC),
                          datetime(1997, 9, 4, 9, 0, tzinfo=NYC)])

    def testRdateWithTZIDMapping(self):
        rr = rrulestr("DTSTART:19970902T090000\n"
                      "RDATE;TZID=Eastern:19970902T090000\n",
                      tzids={'Eastern': NYC})
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0, tzinfo=NYC)])

    def testRdateWithTZIDCallable(self):
        def lookup(name):
            if name == 'UTC+04':
                return tz.tzstr('UTC+04')
            raise ValueError('unknown tzid: %s' % name)

        rr = rrulestr("DTSTART:19970902T090000\n"
                      "RDATE;TZID=UTC+04:19970902T090000\n",
                      tzids=lookup)
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0,
                                    tzinfo=tz.tzstr('UTC+04'))])

    def testRdateValueDate(self):
        rr = rrulestr("DTSTART:19970902T090000\n"
                      "RDATE;VALUE=DATE:19970902\n"
                      "RDATE;VALUE=DATE:19970904\n")
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2), datetime(1997, 9, 4)])

    def testRdateValueDateTime(self):
        rr = rrulestr("DTSTART:19970902T090000\n"
                      "RDATE;VALUE=DATE-TIME:19970902T090000\n"
                      "RDATE;VALUE=DATE-TIME:19970904T090000\n")
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testRdateValueDateWithTZID(self):
        rr = rrulestr("DTSTART:19970902T090000\n"
                      "RDATE;VALUE=DATE;TZID=America/New_York:19970902\n")
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, tzinfo=NYC)])

    def testConflictingTimezoneErrorMessage(self):
        with self.assertRaisesRegex(
                ValueError, "date property specifies multiple timezones"):
            rrulestr("DTSTART;TZID=America/New_York:19970902T090000Z\n"
                     "RRULE:FREQ=YEARLY;COUNT=3\n")


class RRuleStrVCalendarTest(unittest.TestCase):
    def _vcalendar(self, event_body, vtimezone=""):
        return (
            "BEGIN:VCALENDAR\n"
            "VERSION:2.0\n"
            "PRODID:-//Test//EN\n"
            + vtimezone +
            "BEGIN:VEVENT\n"
            + event_body +
            "SUMMARY:Test event\n"
            "END:VEVENT\n"
            "END:VCALENDAR\n"
        )

    def testAutoDetectVCalendar(self):
        ical = self._vcalendar(
            "DTSTART;TZID=America/New_York:19970902T090000\n"
            "RRULE:FREQ=DAILY;COUNT=3\n")
        rr = rrulestr(ical)
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0, tzinfo=NYC),
                          datetime(1997, 9, 3, 9, 0, tzinfo=NYC),
                          datetime(1997, 9, 4, 9, 0, tzinfo=NYC)])

    def testVCalendarWithVTimezone(self):
        ical = self._vcalendar(
            "DTSTART;TZID=America/New_York:19970902T090000\n"
            "RRULE:FREQ=DAILY;COUNT=2\n",
            vtimezone=(
                "BEGIN:VTIMEZONE\n"
                "TZID:America/New_York\n"
                "BEGIN:STANDARD\n"
                "DTSTART:19701101T020000\n"
                "TZOFFSETFROM:-0400\n"
                "TZOFFSETTO:-0500\n"
                "TZNAME:EST\n"
                "END:STANDARD\n"
                "BEGIN:DAYLIGHT\n"
                "DTSTART:19700308T020000\n"
                "TZOFFSETFROM:-0500\n"
                "TZOFFSETTO:-0400\n"
                "TZNAME:EDT\n"
                "END:DAYLIGHT\n"
                "END:VTIMEZONE\n"))
        rr = rrulestr(ical)
        result = list(rr)
        self.assertEqual(len(result), 2)
        # September 2nd 1997 is EDT: UTC-4
        self.assertEqual(result[0].utcoffset(), timedelta(hours=-4))
        self.assertEqual(result[0].replace(tzinfo=None),
                         datetime(1997, 9, 2, 9, 0))

    def testVCalendarInlineVTimezoneTakesPriorityOverTzids(self):
        ical = self._vcalendar(
            "DTSTART;TZID=Eastern:19970902T090000\n"
            "RRULE:FREQ=DAILY;COUNT=1\n",
            vtimezone=(
                "BEGIN:VTIMEZONE\n"
                "TZID:Eastern\n"
                "BEGIN:STANDARD\n"
                "DTSTART:19701101T020000\n"
                "TZOFFSETFROM:-0400\n"
                "TZOFFSETTO:-0500\n"
                "TZNAME:EST\n"
                "END:STANDARD\n"
                "BEGIN:DAYLIGHT\n"
                "DTSTART:19700308T020000\n"
                "TZOFFSETFROM:-0500\n"
                "TZOFFSETTO:-0400\n"
                "TZNAME:EDT\n"
                "END:DAYLIGHT\n"
                "END:VTIMEZONE\n"))
        # The tzids mapping says UTC; the inline VTIMEZONE must win.
        rr = rrulestr(ical, tzids={'Eastern': tz.UTC})
        result = list(rr)
        self.assertEqual(result[0].utcoffset(), timedelta(hours=-4))

    def testVCalendarOnlyFirstVEVENTUsed(self):
        ical = (
            "BEGIN:VCALENDAR\n"
            "BEGIN:VEVENT\n"
            "DTSTART:19970902T090000\n"
            "RRULE:FREQ=DAILY;COUNT=2\n"
            "END:VEVENT\n"
            "BEGIN:VEVENT\n"
            "DTSTART:20010101T000000\n"
            "RRULE:FREQ=DAILY;COUNT=2\n"
            "END:VEVENT\n"
            "END:VCALENDAR\n")
        rr = rrulestr(ical)
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0)])

    def testVCalendarLineUnfolding(self):
        ical = (
            "BEGIN:VCALENDAR\n"
            "BEGIN:VEVENT\n"
            "DTSTART:19970902T090000\n"
            "RRULE:FREQ=DAILY;COUNT=2;BYDAY=MO,TU,WE,TH,FR,\n"
            " SA,SU\n"
            "END:VEVENT\n"
            "END:VCALENDAR\n")
        rr = rrulestr(ical)
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0)])

    def testVCalendarWithRDateAndExDate(self):
        ical = self._vcalendar(
            "DTSTART:19970902T090000\n"
            "RRULE:FREQ=DAILY;COUNT=4\n"
            "RDATE:19970910T090000\n"
            "EXDATE:19970903T090000\n")
        rr = rrulestr(ical)
        self.assertEqual(list(rr),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 4, 9, 0),
                          datetime(1997, 9, 5, 9, 0),
                          datetime(1997, 9, 10, 9, 0)])


class RRuleStrTest(unittest.TestCase):
    def testStrTzAwareDtstart(self):
        rr = rrule(DAILY, count=3,
                   dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=NYC))
        s = str(rr)
        self.assertIn("TZID=", s)
        self.assertIn("19970902T090000", s)
        # Round-trip
        rr2 = rrulestr(s)
        self.assertEqual(list(rr), list(rr2))

    def testStrUtcDtstart(self):
        rr = rrule(DAILY, count=3,
                   dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=tz.UTC))
        s = str(rr)
        self.assertIn("DTSTART:19970902T090000Z", s)
        rr2 = rrulestr(s)
        self.assertEqual(list(rr), list(rr2))

    def testStrAutoGeneratedTzAwareDtstart(self):
        now = datetime.now(tz=NYC).replace(microsecond=0)
        rr = rrule(DAILY, count=2, dtstart=now)
        s = str(rr)
        rr2 = rrulestr(s)
        self.assertEqual(list(rr), list(rr2))

    def testStrUntilUtc(self):
        rr = rrule(DAILY,
                   dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=NYC),
                   until=datetime(1997, 9, 4, 14, 0, tzinfo=tz.UTC))
        s = str(rr)
        self.assertIn("UNTIL=19970904T140000Z", s)

    def testStrUntilNaive(self):
        rr = rrule(DAILY,
                   dtstart=datetime(1997, 9, 2, 9, 0),
                   until=datetime(1997, 9, 4, 14, 0))
        s = str(rr)
        self.assertIn("UNTIL=19970904T140000", s)
        self.assertNotIn("UNTIL=19970904T140000Z", s)


class RRuleEqualityTest(unittest.TestCase):
    def testEq(self):
        a = rrule(DAILY, count=3, dtstart=datetime(1997, 9, 2, 9, 0))
        b = rrule(DAILY, count=3, dtstart=datetime(1997, 9, 2, 9, 0))
        c = rrule(DAILY, count=4, dtstart=datetime(1997, 9, 2, 9, 0))
        d = rrule(WEEKLY, count=3, dtstart=datetime(1997, 9, 2, 9, 0))
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)

    def testHashConsistentWithEq(self):
        a = rrule(DAILY, count=3, dtstart=datetime(1997, 9, 2, 9, 0))
        b = rrule(DAILY, count=3, dtstart=datetime(1997, 9, 2, 9, 0))
        self.assertEqual(hash(a), hash(b))

    def testReprReconstructable(self):
        rr = rrule(WEEKLY, count=3, dtstart=datetime(1997, 9, 2, 9, 0))
        r = repr(rr)
        self.assertIn("WEEKLY", r)
        ns = {'rrule': rrule, 'WEEKLY': WEEKLY,
               'datetime': _dt_module}
        rr2 = eval(r, ns)
        self.assertEqual(list(rr), list(rr2))

    def testReprSymbolicFreqNames(self):
        for freq, name in [(YEARLY, "YEARLY"), (MONTHLY, "MONTHLY"),
                           (WEEKLY, "WEEKLY"), (DAILY, "DAILY"),
                           (HOURLY, "HOURLY"), (MINUTELY, "MINUTELY"),
                           (SECONDLY, "SECONDLY")]:
            rr = rrule(freq, count=2, dtstart=datetime(1997, 9, 2, 9, 0))
            self.assertIn(name, repr(rr))


class RRulePropertiesTest(unittest.TestCase):
    def testProperties(self):
        rr = rrule(MONTHLY, interval=2, count=5,
                   dtstart=datetime(1997, 9, 2, 9, 0))
        self.assertEqual(rr.dtstart, datetime(1997, 9, 2, 9, 0))
        self.assertEqual(rr.freq, MONTHLY)
        self.assertEqual(rr.interval, 2)
        self.assertIsNone(rr.until)

    def testPropertiesUntil(self):
        rr = rrule(DAILY,
                   dtstart=datetime(1997, 9, 2, 9, 0),
                   until=datetime(1997, 9, 5, 9, 0))
        self.assertEqual(rr.until, datetime(1997, 9, 5, 9, 0))

    def testPropertiesReadOnly(self):
        rr = rrule(DAILY, count=3, dtstart=datetime(1997, 9, 2, 9, 0))
        for prop in ("dtstart", "freq", "interval", "until"):
            with self.assertRaises(AttributeError):
                setattr(rr, prop, None)

    def testCountMethod(self):
        rr = rrule(DAILY, count=7, dtstart=datetime(1997, 9, 2, 9, 0))
        self.assertEqual(rr.count(), 7)

    def testCountMethodIteratesWhenNotSet(self):
        rr = rrule(DAILY,
                   dtstart=datetime(1997, 9, 2, 9, 0),
                   until=datetime(1997, 9, 5, 9, 0))
        self.assertEqual(rr.count(), 4)


class RRuleToIcalTest(unittest.TestCase):
    def testToIcalUtc(self):
        rr = rrule(DAILY, count=2,
                   dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=tz.UTC))
        ical = rr.to_ical()
        self.assertIn("BEGIN:VCALENDAR", ical)
        self.assertIn("END:VCALENDAR", ical)
        self.assertIn("BEGIN:VEVENT", ical)
        self.assertIn("END:VEVENT", ical)
        self.assertIn("DTSTART:19970902T090000Z", ical)
        self.assertNotIn("VTIMEZONE", ical)

    def testToIcalNonUtc(self):
        TZ = tz.tzstr('EST5EDT')
        rr = rrule(DAILY, count=2,
                   dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=TZ))
        ical = rr.to_ical()
        self.assertIn("BEGIN:VCALENDAR", ical)
        self.assertIn("BEGIN:VEVENT", ical)
        self.assertIn("BEGIN:VTIMEZONE", ical)
        self.assertIn("END:VTIMEZONE", ical)
        self.assertIn("STANDARD", ical)
        self.assertIn("TZOFFSETFROM", ical)
        self.assertIn("TZOFFSETTO", ical)
        self.assertIn("TZID=", ical)
        self.assertIn("DTSTART", ical)


class RRulesetComponentsTest(unittest.TestCase):
    def _make_set(self):
        rs = rruleset()
        rr = rrule(DAILY, count=3, dtstart=datetime(1997, 9, 2, 9, 0))
        rr2 = rrule(WEEKLY, count=2, dtstart=datetime(1997, 9, 2, 9, 0))
        d = datetime(1997, 9, 5, 9, 0)
        d2 = datetime(1997, 9, 6, 9, 0)
        rs.rrule(rr)
        rs.rdate(d)
        rs.exrule(rr2)
        rs.exdate(d2)
        return rs, rr, rr2, d, d2

    def testComponentAccessors(self):
        rs, rr, rr2, d, d2 = self._make_set()
        self.assertEqual(rs.rrules, (rr,))
        self.assertEqual(rs.rdates, (d,))
        self.assertEqual(rs.exrules, (rr2,))
        self.assertEqual(rs.exdates, (d2,))

    def testComponentAccessorsReadOnly(self):
        rs, *_ = self._make_set()
        for prop in ("rrules", "rdates", "exrules", "exdates"):
            with self.assertRaises(AttributeError):
                setattr(rs, prop, ())

    def testEq(self):
        a, rr, rr2, d, d2 = self._make_set()
        b = rruleset()
        # Different insertion order, same components
        b.exdate(d2)
        b.exrule(rr2)
        b.rdate(d)
        b.rrule(rr)
        self.assertEqual(a, b)

        c = rruleset()
        c.rrule(rr)
        self.assertNotEqual(a, c)

    def testEqDatesOrderIndependent(self):
        a = rruleset()
        a.rdate(datetime(1997, 9, 2, 9, 0))
        a.rdate(datetime(1997, 9, 5, 9, 0))
        b = rruleset()
        b.rdate(datetime(1997, 9, 5, 9, 0))
        b.rdate(datetime(1997, 9, 2, 9, 0))
        self.assertEqual(a, b)

    def testRepr(self):
        rs, rr, rr2, d, d2 = self._make_set()
        r = repr(rs)
        self.assertTrue(r.startswith("rruleset()"))
        self.assertIn("\n", r)
        self.assertIn(".rrule(", r)
        self.assertIn(".rdate(", r)
        self.assertIn(".exrule(", r)
        self.assertIn(".exdate(", r)

    def testCopy(self):
        rs, rr, rr2, d, d2 = self._make_set()
        rs2 = rs.copy()
        self.assertIsNot(rs2, rs)
        self.assertEqual(rs2.rrules, rs.rrules)
        self.assertEqual(rs2.rdates, rs.rdates)
        self.assertEqual(rs2.exrules, rs.exrules)
        self.assertEqual(rs2.exdates, rs.exdates)
        self.assertEqual(list(rs2), list(rs))

    def testUnion(self):
        a = rruleset()
        a.rrule(rrule(DAILY, count=2, dtstart=datetime(1997, 9, 2, 9, 0)))
        b = rruleset()
        b.rdate(datetime(1997, 9, 5, 9, 0))
        u = a.union(b)
        self.assertEqual(u.rrules, a.rrules + b.rrules)
        self.assertEqual(u.rdates, a.rdates + b.rdates)
        self.assertEqual(u.exrules, a.exrules + b.exrules)
        self.assertEqual(u.exdates, a.exdates + b.exdates)
        self.assertEqual(list(u),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 5, 9, 0)])

    def testUnionTypeError(self):
        a = rruleset()
        with self.assertRaises(TypeError):
            a.union(rrule(DAILY, count=2,
                          dtstart=datetime(1997, 9, 2, 9, 0)))

    def testSubtract(self):
        a = rruleset()
        a.rrule(rrule(DAILY, count=4, dtstart=datetime(1997, 9, 2, 9, 0)))
        b = rruleset()
        b.rrule(rrule(WEEKLY, count=2, dtstart=datetime(1997, 9, 2, 9, 0)))
        b.rdate(datetime(1997, 9, 5, 9, 0))
        s = a.subtract(b)
        self.assertEqual(s.exrules, b.rrules)
        self.assertEqual(s.exdates, b.rdates)
        # 1997-09-02 (exrule) and 1997-09-05 (exdate) are excluded
        self.assertEqual(list(s),
                         [datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])

    def testSubtractTypeError(self):
        a = rruleset()
        with self.assertRaises(TypeError):
            a.subtract(rrule(DAILY, count=2,
                             dtstart=datetime(1997, 9, 2, 9, 0)))

    def testToIcal(self):
        TZ1 = tz.tzstr('EST5EDT')
        TZ2 = tz.tzstr('CET1CEST')
        rs = rruleset()
        rs.rrule(rrule(DAILY, count=2,
                       dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=TZ1)))
        rs.rdate(datetime(1997, 9, 5, 9, 0, tzinfo=TZ2))
        ical = rs.to_ical()
        self.assertIn("BEGIN:VCALENDAR", ical)
        self.assertIn("END:VCALENDAR", ical)
        # One VTIMEZONE block per unique non-UTC timezone
        self.assertEqual(ical.count("BEGIN:VTIMEZONE"), 2)
        self.assertEqual(ical.count("END:VTIMEZONE"), 2)

    def testToIcalUtcNoVTimezone(self):
        rs = rruleset()
        rs.rrule(rrule(DAILY, count=2,
                       dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=tz.UTC)))
        ical = rs.to_ical()
        self.assertIn("BEGIN:VCALENDAR", ical)
        self.assertNotIn("VTIMEZONE", ical)

    def testFromStr(self):
        rs = rruleset.from_str(
            "DTSTART:19970902T090000\n"
            "RRULE:FREQ=DAILY;COUNT=3\n")
        self.assertIsInstance(rs, rruleset)
        self.assertEqual(list(rs),
                         [datetime(1997, 9, 2, 9, 0),
                          datetime(1997, 9, 3, 9, 0),
                          datetime(1997, 9, 4, 9, 0)])


class RRulesetStrTest(unittest.TestCase):
    def testStrOrderAndTzid(self):
        rs = rruleset()
        rs.rrule(rrule(DAILY, count=3,
                       dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=NYC)))
        rs.rdate(datetime(1997, 9, 5, 9, 0, tzinfo=NYC))
        rs.exrule(rrule(WEEKLY, count=2,
                        dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=NYC)))
        rs.exdate(datetime(1997, 9, 3, 9, 0, tzinfo=NYC))
        s = str(rs)
        lines = s.splitlines()
        self.assertTrue(lines[0].startswith("DTSTART"))
        self.assertIn("TZID=", lines[0])
        idx_rrule = next(i for i, l in enumerate(lines)
                         if l.startswith("RRULE:"))
        idx_rdate = next(i for i, l in enumerate(lines)
                         if l.startswith("RDATE"))
        idx_exrule = next(i for i, l in enumerate(lines)
                          if l.startswith("EXRULE:"))
        idx_exdate = next(i for i, l in enumerate(lines)
                          if l.startswith("EXDATE"))
        self.assertLess(idx_rrule, idx_rdate)
        self.assertLess(idx_rdate, idx_exrule)
        self.assertLess(idx_exrule, idx_exdate)

    def testStrUtcZSuffix(self):
        rs = rruleset()
        rs.rrule(rrule(DAILY, count=2,
                       dtstart=datetime(1997, 9, 2, 9, 0, tzinfo=tz.UTC)))
        rs.rdate(datetime(1997, 9, 5, 9, 0, tzinfo=tz.UTC))
        s = str(rs)
        lines = s.splitlines()
        self.assertTrue(lines[0].startswith("DTSTART:19970902T090000Z"))
        rdate_line = next(l for l in lines if l.startswith("RDATE"))
        self.assertIn("19970905T090000Z", rdate_line)


if __name__ == '__main__':
    unittest.main()
