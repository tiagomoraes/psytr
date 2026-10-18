#!/usr/bin/env python3
"""Tests for week_collect.py — run with `python3 -m unittest discover -s scripts`."""

import os
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import week_collect as wc  # noqa: E402

TZ = ZoneInfo("America/Recife")  # UTC-3, used as the "local" timezone in fixtures

ENTRIES_MD = """# Entries — 2026-10

Append-only: new entries go at the END of this file.

<!--
## entry-2020-01-01-999
- ts: 2020-01-01T00:00:00Z
- title: commented example — must be ignored
-->

## entry-2026-10-14-001
- ts: 2026-10-14T21:30:00Z
- title: Difficult conversation with the team
- situation: planning meeting, tight deadline, client pressure
- thoughts: "I won't be able to handle it" ; "I'm going to let everyone down"
- emotions: anxiety: 80 ; frustration: 60
- body: tightness in the chest
- behavior: kept working in silence
- context: slept 6h
- tags: work, health

## entry-2026-10-16-002
- ts: 2026-10-16T18:13:00Z
- title: Conversation with a friend
- situation: I had a conversation with a friend
- thoughts: "they were upset with me"
- emotions: sadness: 70 ; fatigue: 50
- body: fatigue
- behavior: went to bed early
- tags: friends

## entry-2026-10-16-003
- ts: 2026-10-19T02:59:00Z
- title: Sunday night (23:59 local) — Monday UTC
- situation: week boundary
- emotions: relief: 40
- tags: test

## entry-2026-10-25-004
- ts: 2026-10-25T12:00:00Z
- title: Out of the week (next week)
- emotions: joy: 90
- tags: test
"""

CHECKINS_MD = """# Check-ins — 2026-10

## checkin-2026-10-13
- ts: 2026-10-13T12:00:30Z
- mood: 3/5
- energy: 3/5
- anxiety: 4/5
- sleep_h: 6
- sleep_quality: poor
- note: heavy day

## checkin-2026-10-16
- ts: 2026-10-16T12:01:00Z
- mood: 4/5
- sleep_h: 7.5

## checkin-2026-10-18
- ts: 2026-10-18T23:50:00Z
- mood: 5/5

## checkin-2026-10-19
- ts: 2026-10-19T12:00:00Z
- mood: 1/5
"""

CONFIG_MD = """# sintr config

- name: Test Person
- language: en
- timezone: America/Recife
- require_approval: true
"""


def make_ledger(tmp: str) -> Path:
    ledger = Path(tmp) / "sintr"
    (ledger / "entries").mkdir(parents=True)
    (ledger / "checkins").mkdir(parents=True)
    (ledger / "config.md").write_text(CONFIG_MD, encoding="utf-8")
    (ledger / "entries" / "2026-10.md").write_text(ENTRIES_MD, encoding="utf-8")
    (ledger / "checkins" / "2026-10.md").write_text(CHECKINS_MD, encoding="utf-8")
    return ledger


class TestParsing(unittest.TestCase):
    def test_parse_emotions_colon_and_space(self):
        em, warn = wc.parse_emotions("anxiety: 80 ; sadness 70")
        self.assertEqual(em, [("anxiety", 80), ("sadness", 70)])
        self.assertEqual(warn, [])

    def test_parse_emotions_bad_chunk(self):
        em, warn = wc.parse_emotions("anxiety: 80 ; ???")
        self.assertEqual(em, [("anxiety", 80)])
        self.assertEqual(len(warn), 1)

    def test_parse_ts_variants(self):
        self.assertEqual(wc.parse_ts("2026-10-14T21:30:00Z").hour, 21)
        self.assertEqual(wc.parse_ts("2026-10-14").hour, 12)  # date-only -> noon
        self.assertIsNone(wc.parse_ts("garbage"))
        self.assertIsNone(wc.parse_ts(""))

    def test_parse_rating(self):
        self.assertEqual(wc.parse_rating("4/5"), 4.0)
        self.assertEqual(wc.parse_rating("4.5/5"), 4.5)
        self.assertEqual(wc.parse_rating("4,5/5"), 4.5)
        self.assertEqual(wc.parse_rating("4"), 4.0)
        self.assertEqual(wc.parse_rating("7/10"), 3.5)  # another scale is brought to 5
        self.assertIsNone(wc.parse_rating("8"))         # out of range without a scale
        self.assertIsNone(wc.parse_rating(""))

    def test_parse_sleep_h(self):
        self.assertEqual(wc.parse_sleep_h("7"), 7.0)
        self.assertEqual(wc.parse_sleep_h("6,5"), 6.5)
        self.assertEqual(wc.parse_sleep_h("7h30"), 7.5)
        self.assertEqual(wc.parse_sleep_h("7:30"), 7.5)
        self.assertEqual(wc.parse_sleep_h("5.5h"), 5.5)
        self.assertIsNone(wc.parse_sleep_h("30"))
        self.assertIsNone(wc.parse_sleep_h("muito"))

    def test_comments_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            entries, _ = wc.parse_entries(ledger)
            ids = [e["id"] for e in entries]
            self.assertNotIn("entry-2020-01-01-999", ids)

    def test_entries_parsed_with_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            entries, warn = wc.parse_entries(ledger)
            self.assertEqual(len(entries), 4)
            first = entries[0]
            self.assertEqual(first["id"], "entry-2026-10-14-001")
            self.assertEqual(first["emotions"], [("anxiety", 80), ("frustration", 60)])
            self.assertEqual(first["tags"], ["work", "health"])
            self.assertEqual(warn, [])

    def test_checkins_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            checkins, _ = wc.parse_checkins(ledger)
            self.assertEqual(len(checkins), 4)
            self.assertEqual(checkins[0]["mood"], 3.0)
            self.assertEqual(checkins[0]["sleep_h"], 6.0)
            self.assertIsNone(checkins[1]["energy"])

    def test_unicode_values_roundtrip(self):
        # Ledger *values* live in the owner's language; the pack must handle them.
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            p = ledger / "entries" / "2026-10.md"
            p.write_text(p.read_text(encoding="utf-8") + """
## entry-2026-10-15-005
- ts: 2026-10-15T14:00:00Z
- title: Conversa difícil — acentuação
- thoughts: "não vou dar conta"
- emotions: ansiedade: 80 ; frustração: 60
- tags: trabalho, saúde
""", encoding="utf-8")
            entries, _ = wc.parse_entries(ledger)
            u = [e for e in entries if e["id"] == "entry-2026-10-15-005"][0]
            self.assertEqual(u["emotions"], [("ansiedade", 80), ("frustração", 60)])
            self.assertEqual(u["tags"], ["trabalho", "saúde"])


class TestWeekResolution(unittest.TestCase):
    def test_resolve_explicit_week(self):
        start, end, label = wc.resolve_week("2026-W42", TZ)
        self.assertEqual(label, "2026-W42")
        self.assertEqual(start.date(), date(2026, 10, 12))
        self.assertEqual((end - start).days, 7)

    def test_resolve_invalid(self):
        with self.assertRaises(SystemExit):
            wc.resolve_week("banana", TZ)


class TestFilteringAndRender(unittest.TestCase):
    def digest(self, tmp, week="2026-W42"):
        ledger = make_ledger(tmp)
        return ledger, wc.build_digest(ledger, week, None)

    def test_week_filter_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger, digest = self.digest(tmp)
            # ts 2026-10-19T02:59Z == Sunday 2026-10-18 23:59 local (UTC-3) -> still week 42
            self.assertIn("entry-2026-10-16-003", digest)
            # week 43 entry must NOT appear
            self.assertNotIn("entry-2026-10-25-004", digest)
            # check-in at 2026-10-18T23:50Z (Sunday 20:50 local) is in week 42
            self.assertIn("| 2026-10-18 | 5/5 |", digest)
            # check-in 2026-10-19T12:00Z is Monday week 43 -> out
            self.assertNotIn("| 2026-10-19 |", digest)
            # summary count: 3 entries, 3 check-ins in week 42
            self.assertIn("entries: 3 · check-ins: 3", digest)

    def test_render_sections_and_aggregates(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, digest = self.digest(tmp)
            for section in ["## Check-ins", "### Check-in aggregates",
                            "## Entries", "## Emotion frequency", "## Tag frequency",
                            "## Raw entries"]:
                self.assertIn(section, digest)
            self.assertIn("anxiety: 1x", digest)  # emotion frequency counts entries only
            self.assertIn("work: 1x", digest)

    def test_empty_week(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            digest = wc.build_digest(ledger, "2026-W01", None)
            self.assertIn("Empty week", digest)

    def test_warning_on_bad_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            p = ledger / "entries" / "2026-10.md"
            p.write_text(p.read_text(encoding="utf-8") + "\n## entry-2026-10-15-999\n- title: no ts\n", encoding="utf-8")
            digest = wc.build_digest(ledger, "2026-W42", None)
            self.assertIn("no parseable ts", digest)


SESSION_CFG = {"timezone": "America/Recife", "session_day": "Monday", "session_time": "18:00", "report_lead": "1h"}


class TestSessionPeriod(unittest.TestCase):
    def at(self, *args):
        return datetime(*args, tzinfo=TZ)

    def test_parse_lead(self):
        self.assertEqual(wc.parse_lead("1h"), wc.timedelta(hours=1))
        self.assertEqual(wc.parse_lead("90min"), wc.timedelta(minutes=90))
        self.assertEqual(wc.parse_lead("1h30"), wc.timedelta(minutes=90))
        self.assertEqual(wc.parse_lead("45m"), wc.timedelta(minutes=45))
        self.assertEqual(wc.parse_lead(""), wc.timedelta(hours=1))
        self.assertEqual(wc.parse_lead("soon"), wc.timedelta(hours=1))

    def test_parse_clock(self):
        self.assertEqual(wc.parse_clock("18:00"), (18, 0))
        self.assertEqual(wc.parse_clock("18h"), (18, 0))
        self.assertEqual(wc.parse_clock("9h30"), (9, 30))
        self.assertIsNone(wc.parse_clock("evening"))

    def test_next_and_last(self):
        before = self.at(2026, 10, 19, 17, 5)  # Monday, 55 minutes before the session
        self.assertEqual(wc.resolve_session("next", TZ, SESSION_CFG, before), self.at(2026, 10, 19, 18, 0))
        self.assertEqual(wc.resolve_session("last", TZ, SESSION_CFG, before), self.at(2026, 10, 12, 18, 0))
        after = self.at(2026, 10, 19, 18, 30)
        self.assertEqual(wc.resolve_session("next", TZ, SESSION_CFG, after), self.at(2026, 10, 26, 18, 0))
        self.assertEqual(wc.resolve_session("last", TZ, SESSION_CFG, after), self.at(2026, 10, 19, 18, 0))

    def test_explicit_and_rescheduled(self):
        self.assertEqual(wc.resolve_session("2026-10-21", TZ, SESSION_CFG), self.at(2026, 10, 21, 18, 0))
        self.assertEqual(wc.resolve_session("2026-10-22T19:30", TZ, SESSION_CFG), self.at(2026, 10, 22, 19, 30))
        with self.assertRaises(SystemExit):
            wc.resolve_session("next", TZ, {"timezone": "UTC"})
        with self.assertRaises(SystemExit):
            wc.resolve_session("2026-10-21", TZ, {"session_day": "Monday"})  # no time anywhere

    def test_period_ends_lead_before_the_session(self):
        p = wc.resolve_period(SESSION_CFG, TZ, session="2026-10-19")
        self.assertEqual((p["kind"], p["label"]), ("session", "2026-10-19"))
        self.assertEqual(p["end"], self.at(2026, 10, 19, 17, 0))
        self.assertEqual(p["start"], self.at(2026, 10, 12, 17, 0))

    def test_consecutive_reports_meet(self):
        a = wc.resolve_period(SESSION_CFG, TZ, session="2026-10-12")
        b = wc.resolve_period(SESSION_CFG, TZ, session="2026-10-19")
        self.assertEqual(a["end"], b["start"])  # no gap, no overlap

    def test_lead_across_midnight(self):
        cfg = dict(SESSION_CFG, session_time="00:30")
        p = wc.resolve_period(cfg, TZ, session="2026-10-19")
        self.assertEqual(p["end"], self.at(2026, 10, 18, 23, 30))

    def test_default_follows_the_config(self):
        self.assertEqual(wc.resolve_period(SESSION_CFG, TZ, now=self.at(2026, 10, 19, 17, 5))["label"], "2026-10-19")
        self.assertEqual(wc.resolve_period({"timezone": "UTC"}, TZ)["kind"], "week")

    def test_schedule(self):
        text, ok = wc.schedule(SESSION_CFG, TZ, now=self.at(2026, 10, 14, 9, 0))
        self.assertTrue(ok)
        self.assertIn("Mondays at 17:00", text)
        self.assertIn("CRON_TZ=America/Recife", text)
        self.assertIn("0 17 * * 1", text)
        self.assertIn("reports/2026-10-19.md", text)
        self.assertFalse(wc.schedule({"timezone": "UTC"}, TZ)[1])

    def test_config_values_ignore_trailing_notes(self):
        # people fill the template in place, so its notes stay after their values
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            (ledger / "config.md").write_text(
                "- timezone: America/Recife\n"
                "- session_day: terça                    # e.g. Wednesday\n"
                "- session_time: 11:00              # normalmente\n"
                "- report_lead: 1h                 # how long before the session the report is prepared\n",
                encoding="utf-8")
            cfg = wc.read_config(ledger)
            self.assertEqual((cfg["session_day"], cfg["session_time"], cfg["report_lead"]), ("terça", "11:00", "1h"))
            text, ok = wc.schedule(cfg, TZ, now=self.at(2026, 10, 18, 20, 0))
            self.assertTrue(ok)
            self.assertIn("Tuesdays at 10:00", text)

    def test_template_config_parses(self):
        # the shipped template, filled in place, must not leak its notes into values
        template = Path(__file__).resolve().parent.parent / "templates" / "sintr" / "config.md"
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            text = template.read_text(encoding="utf-8")
            text = text.replace("- session_day: ", "- session_day: Monday").replace("- session_time: ", "- session_time: 18:00")
            (ledger / "config.md").write_text(text, encoding="utf-8")
            cfg = wc.read_config(ledger)
            self.assertNotIn("#", "".join(cfg.values()))
            self.assertEqual(wc.resolve_period(cfg, TZ, now=self.at(2026, 10, 19, 9, 0))["label"], "2026-10-19")

    def test_session_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            (ledger / "config.md").write_text(CONFIG_MD + "- session_day: Monday\n- session_time: 18:00\n", encoding="utf-8")
            digest = wc.build_digest(ledger, None, None, session="2026-10-19")
            self.assertIn("session of 2026-10-19", digest)
            # the period runs Mon 12 17:00 -> Mon 19 17:00: Tuesday 13th is in
            self.assertIn("| 2026-10-13 |", digest)
            self.assertIn("| 2026-10-19 | 1/5 |", digest)  # the morning of the session day counts


class TestConfigDefault(unittest.TestCase):
    def test_tz_from_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = make_ledger(tmp)
            cfg = wc.read_config(ledger)
            self.assertEqual(cfg["timezone"], "America/Recife")
            self.assertEqual(cfg["require_approval"], "true")


if __name__ == "__main__":
    unittest.main()
