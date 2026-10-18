#!/usr/bin/env python3
"""sintr — weekly digest collector.

Reads a sintr ledger and emits a Markdown digest for one ISO week:

- every check-in in range (mood/energy/anxiety/sleep) plus averages;
- every structured entry in range (title, situation, emotions, tags);
- mechanical aggregates: counts, emotion frequency with average intensity,
  tag frequency;
- the full raw entry blocks, so a downstream agent can write the weekly
  report without re-reading the ledger.

Deterministic and stdlib-only. The agent writes prose on top of these facts;
this script never interprets, diagnoses, or invents.

Notes:
- Timestamps in the ledger are UTC ISO 8601. A date-only value is accepted
  and interpreted as 12:00 UTC (noon, so it never lands on a day boundary).
- Week ranges are computed in the ledger's timezone (config.md `timezone:`,
  overridable with --tz).
- A report is for a therapy session by default (config.md `session_day` and
  `session_time`): it covers the 7 days that end `report_lead` (default 1h)
  before the session, so it is fresh for the session and consecutive weekly
  reports meet with no gap and no overlap. `--week` keeps the calendar week
  (Monday to Sunday) for people without a fixed session. `--schedule` prints
  when to prepare the report and a cron line for it.
- Exit codes: 0 = digest produced (even for an empty week); 2 = usage error.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python < 3.9
    ZoneInfo = None


FIELD_RE = re.compile(r"^\s*-\s*([a-z_]+)\s*:\s*(.*)$")
COMMENT_RE = re.compile(r"<!--.*?-->", flags=re.S)
EMOTION_COLON_RE = re.compile(r"^(.+?):\s*(\d{1,3})\s*$")
EMOTION_SPACE_RE = re.compile(r"^(.+?)\s+(\d{1,3})\s*$")
WEEK_RE = re.compile(r"^(\d{4})-W(\d{1,2})$")
SESSION_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:[T ](\d{1,2}):(\d{2}))?$")
CLOCK_RE = re.compile(r"^(\d{1,2})(?::(\d{2})|h(\d{2})?)$")
WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
    "segunda": 0, "terça": 1, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sábado": 5, "sabado": 5,
    "domingo": 6,
}
WEEKDAY_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DEFAULT_LEAD = timedelta(hours=1)

ENTRY_KNOWN = {
    "ts", "title", "situation", "thoughts", "emotions", "body", "behavior",
    "context", "tags", "notes",
}
CHECKIN_KNOWN = {
    "ts", "mood", "energy", "anxiety", "sleep_h", "sleep_quality", "note",
}


# --------------------------------------------------------------------------
# low-level parsing helpers
# --------------------------------------------------------------------------

def strip_comments(text: str) -> str:
    return COMMENT_RE.sub("", text)


def parse_fields(lines) -> dict:
    """Parse `- key: value` bullet fields; indented/non-bullet lines continue
    the previous field's value."""
    fields: dict[str, str] = {}
    current = None
    for line in lines:
        m = FIELD_RE.match(line)
        if m:
            current = m.group(1).strip()
            value = m.group(2).strip()
            if current in fields:
                fields[current] = (fields[current] + " ; " + value).strip(" ;")
            else:
                fields[current] = value
        elif current and line.strip():
            fields[current] = (fields[current] + " " + line.strip()).strip()
    return fields


def parse_ts(raw: str):
    """Parse an ISO 8601 timestamp; date-only means 12:00 UTC. Returns an
    aware datetime in UTC, or None."""
    raw = (raw or "").strip()
    if not raw or raw.lower() == "unknown":
        return None
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            d = date.fromisoformat(raw)
            return datetime(d.year, d.month, d.day, 12, 0, 0, tzinfo=timezone.utc)
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def parse_emotions(raw: str):
    """Parse `ansiedade: 80 ; frustração: 60` (also tolerates `ansiedade 80`).
    Returns (list[(name, int)], warnings)."""
    out, warnings = [], []
    for chunk in (raw or "").split(";"):
        chunk = chunk.strip().strip(",").strip()
        if not chunk:
            continue
        m = EMOTION_COLON_RE.match(chunk) or EMOTION_SPACE_RE.match(chunk)
        if not m:
            warnings.append(f"emotion not parsed: {chunk!r}")
            continue
        name = m.group(1).strip().strip('"').strip("'")
        value = int(m.group(2))
        out.append((name, value))
    return out, warnings


def _number(text: str) -> float:
    return float(text.replace(",", "."))


def parse_rating(raw: str):
    """A 1–5 check-in score. `4/5` -> 4.0, `4` -> 4.0, `4.5/5` and `4,5/5` ->
    4.5; another scale is brought to 5 (`7/10` -> 3.5). None if missing,
    invalid, or outside 0–5."""
    raw = (raw or "").strip()
    if not raw or raw.lower() == "unknown":
        return None
    m = re.match(r"^([0-9]+(?:[.,][0-9]+)?)\s*(?:/\s*([0-9]+))?", raw)
    if not m:
        return None
    value = _number(m.group(1))
    scale = int(m.group(2)) if m.group(2) else 5
    if scale <= 0:
        return None
    value = round(value * 5 / scale, 2) if scale != 5 else value
    return value if 0 <= value <= 5 else None


def parse_sleep_h(raw: str):
    """Hours slept: `7`, `7.5`, `7,5`, `7h30`, `7:30` -> 7.0/7.5. None if
    missing or outside 0–16."""
    raw = (raw or "").strip().lower()
    m = re.match(r"^([0-9]{1,2})\s*(?:h|:)\s*([0-9]{2})\b", raw)
    if m:
        value = int(m.group(1)) + int(m.group(2)) / 60
    else:
        m = re.match(r"^([0-9]+(?:[.,][0-9]+)?)", raw)
        if not m:
            return None
        value = _number(m.group(1))
    return value if 0 <= value <= 16 else None


# --------------------------------------------------------------------------
# ledger reading
# --------------------------------------------------------------------------

def read_config(ledger: Path) -> dict:
    cfg = {}
    path = ledger / "config.md"
    if not path.exists():
        return cfg
    for line in strip_comments(path.read_text(encoding="utf-8")).splitlines():
        m = FIELD_RE.match(line)
        if m:
            # the template's notes follow the value (`- session_time: 18:00   # e.g. …`),
            # or stand alone on an empty field (`- report_day:   # only without …`)
            cfg.setdefault(m.group(1).strip(), re.sub(r"(^|\s+)#.*$", "", m.group(2)).strip())
    return cfg


def _split_blocks(path: Path, prefix: str):
    if not path.exists():
        return []
    text = strip_comments(path.read_text(encoding="utf-8"))
    blocks = re.split(r"(?m)^##\s+", text)[1:]
    out = []
    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        header = lines[0].strip()
        if header.startswith(prefix):
            out.append((header, lines[1:]))
    return out


def parse_entries(ledger: Path):
    entries, warnings = [], []
    for path in sorted(ledger.glob("entries/*.md")):
        if path.name == "YYYY-MM.md":
            continue
        for header, lines in _split_blocks(path, "entry-"):
            fields = parse_fields(lines)
            ts = parse_ts(fields.get("ts", ""))
            if ts is None:
                warnings.append(f"{path.name}: entry {header!r} has no parseable ts — skipped")
                continue
            emotions, ew = parse_emotions(fields.get("emotions", ""))
            warnings.extend(f"{path.name}: {header}: {w}" for w in ew)
            entries.append({
                "id": header,
                "ts": ts,
                "title": fields.get("title", ""),
                "situation": fields.get("situation", ""),
                "thoughts": fields.get("thoughts", ""),
                "emotions": emotions,
                "body": fields.get("body", ""),
                "behavior": fields.get("behavior", ""),
                "context": fields.get("context", ""),
                "tags": [t.strip() for t in fields.get("tags", "").split(",") if t.strip()],
                "notes": fields.get("notes", ""),
                "extra": {k: v for k, v in fields.items() if k not in ENTRY_KNOWN},
                "raw": "## " + header + "\n" + "\n".join(lines).rstrip(),
            })
    entries.sort(key=lambda e: (e["ts"], e["id"]))
    return entries, warnings


def parse_checkins(ledger: Path):
    checkins, warnings = [], []
    for path in sorted(ledger.glob("checkins/*.md")):
        if path.name == "YYYY-MM.md":
            continue
        for header, lines in _split_blocks(path, "checkin-"):
            fields = parse_fields(lines)
            ts = parse_ts(fields.get("ts", ""))
            if ts is None:
                warnings.append(f"{path.name}: check-in {header!r} has no parseable ts — skipped")
                continue
            checkins.append({
                "id": header,
                "ts": ts,
                "mood": parse_rating(fields.get("mood", "")),
                "energy": parse_rating(fields.get("energy", "")),
                "anxiety": parse_rating(fields.get("anxiety", "")),
                "sleep_h": parse_sleep_h(fields.get("sleep_h", "")),
                "sleep_quality": fields.get("sleep_quality", ""),
                "note": fields.get("note", ""),
            })
    checkins.sort(key=lambda c: (c["ts"], c["id"]))
    return checkins, warnings


# --------------------------------------------------------------------------
# week resolution
# --------------------------------------------------------------------------

def resolve_week(spec: str, tz):
    """Return (start, end, label) for an ISO week, as aware datetimes in tz.
    spec: 'this' | 'last' | 'YYYY-Www'."""
    today = datetime.now(tz).date()
    if spec in ("this", None, ""):
        ref = today
    elif spec == "last":
        ref = today - timedelta(days=7)
    else:
        m = WEEK_RE.match(str(spec).strip())
        if not m:
            raise SystemExit(f"sintr: invalid --week value {spec!r} (use 'this', 'last' or YYYY-Www)")
        year, week = int(m.group(1)), int(m.group(2))
        try:
            ref = date.fromisocalendar(year, week, 1)
        except ValueError:
            raise SystemExit(f"sintr: invalid ISO week {spec!r}")
    iso = ref.isocalendar()
    monday = date.fromisocalendar(iso[0], iso[1], 1)
    start = datetime.combine(monday, datetime.min.time(), tzinfo=tz)
    end = start + timedelta(days=7)
    return start, end, f"{iso[0]}-W{iso[1]:02d}"


def parse_lead(raw: str) -> timedelta:
    """How long before the session the report is prepared: `1h`, `90min`,
    `1h30`, `45m`, `2 h`. Empty or unreadable -> 1 hour."""
    raw = (raw or "").strip().lower().replace(" ", "")
    m = re.fullmatch(r"(?:(\d+)h)?(?:(\d+)(?:m|min)?)?", raw)
    if not raw or not m or not (m.group(1) or m.group(2)):
        return DEFAULT_LEAD
    return timedelta(hours=int(m.group(1) or 0), minutes=int(m.group(2) or 0))


def session_weekday(cfg: dict):
    raw = (cfg.get("session_day") or "").strip().lower()
    return WEEKDAYS.get(raw.split()[0].rstrip(",")) if raw else None


def parse_clock(raw: str):
    """`18:00`, `18h`, `18h30` -> (18, 0) / (18, 30); None if unreadable."""
    m = CLOCK_RE.match((raw or "").strip().lower())
    if not m:
        return None
    h, mm = int(m.group(1)), int(m.group(2) or m.group(3) or 0)
    return (h, mm) if h < 24 and mm < 60 else None


def resolve_session(spec: str, tz, cfg: dict, now=None) -> datetime:
    """The session a report is for, as an aware datetime in tz.
    spec: 'next' (the first session that has not started), 'last' (the most
    recent one that has), 'YYYY-MM-DD' (that day, at session_time) or
    'YYYY-MM-DDTHH:MM' (a rescheduled session)."""
    now = (now or datetime.now(tz)).astimezone(tz)
    clock = parse_clock(cfg.get("session_time", ""))
    m = SESSION_RE.match(str(spec).strip())
    if m:
        try:
            day = date.fromisoformat(m.group(1))
        except ValueError:
            raise SystemExit(f"sintr: invalid session date {spec!r}")
        if m.group(2):
            clock = (int(m.group(2)), int(m.group(3)))
        if clock is None:
            raise SystemExit("sintr: no session time: set session_time in config.md or pass YYYY-MM-DDTHH:MM")
        return datetime(day.year, day.month, day.day, clock[0], clock[1], tzinfo=tz)
    if spec not in ("next", "last"):
        raise SystemExit(f"sintr: invalid --session value {spec!r} (use next, last, YYYY-MM-DD or YYYY-MM-DDTHH:MM)")
    weekday = session_weekday(cfg)
    if weekday is None or clock is None:
        raise SystemExit("sintr: session_day and session_time are not set in config.md "
                         "(ask the person when their session usually is), or pass --week")
    day = now.date() + timedelta(days=(weekday - now.weekday()) % 7)
    session = datetime(day.year, day.month, day.day, clock[0], clock[1], tzinfo=tz)
    if spec == "next" and session <= now:
        session += timedelta(days=7)
    if spec == "last" and session > now:
        session -= timedelta(days=7)
    return session


def resolve_period(cfg: dict, tz, week=None, session=None, now=None) -> dict:
    """The span a report covers. With a session (the default when config.md
    has session_day and session_time): the 7 days that end report_lead before
    it, labeled by the session's date. Otherwise the ISO week."""
    if week is None and session is None:
        configured = session_weekday(cfg) is not None and parse_clock(cfg.get("session_time", ""))
        session, week = ("next", None) if configured else (None, "this")
    if session is not None:
        when = resolve_session(session, tz, cfg, now)
        end = when - parse_lead(cfg.get("report_lead", ""))
        return {"kind": "session", "label": when.date().isoformat(), "start": end - timedelta(days=7),
                "end": end, "session": when}
    start, end, label = resolve_week(week, tz)
    return {"kind": "week", "label": label, "start": start, "end": end, "session": None}


def schedule(cfg: dict, tz, now=None):
    """When to prepare the weekly report, from config.md. Returns (text, ok)."""
    weekday, clock = session_weekday(cfg), parse_clock(cfg.get("session_time", ""))
    if weekday is None or clock is None:
        return ("session_day and session_time are not set in config.md. Ask the person when their\n"
                "therapy session usually is (e.g. Wednesday, 18:00) and write both there; the report is\n"
                "then prepared report_lead (default 1h) before it. Without a fixed session, use\n"
                "report_day/report_time and --week instead.", False)
    period = resolve_period(cfg, tz, session="next", now=now)
    lead = parse_lead(cfg.get("report_lead", ""))
    when, start, end = period["session"], period["start"], period["end"]
    local = end.astimezone()  # this machine's timezone, for a plain crontab
    lead_txt = f"{lead.seconds // 3600}h{(lead.seconds % 3600) // 60:02d}".replace("h00", "h")
    text = "\n".join([
        f"session:  {WEEKDAY_EN[when.weekday()]}s at {when:%H:%M} ({tz})",
        f"report:   {WEEKDAY_EN[end.weekday()]}s at {end:%H:%M} ({tz}), report_lead {lead_txt} before the session",
        f"next:     {end:%Y-%m-%d %H:%M} for the session of {when:%Y-%m-%d %H:%M}",
        f"covers:   {start:%Y-%m-%d %H:%M} → {end:%Y-%m-%d %H:%M}, file reports/{period['label']}.md",
        "",
        "cron, in the ledger's timezone (cronie, systemd timers):",
        f"  CRON_TZ={tz}",
        f"  {end.minute} {end.hour} * * {(end.weekday() + 1) % 7}",
        f"cron, in this machine's timezone ({local.tzname()}):",
        f"  {local.minute} {local.hour} * * {(local.weekday() + 1) % 7}",
    ])
    return text, True


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def fmt_emotions(emotions) -> str:
    return " ; ".join(f"{name}: {value}" for name, value in emotions)


def fmt_ts_local(ts, tz) -> str:
    return ts.astimezone(tz).strftime("%Y-%m-%d %H:%M")


def _avg(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return sum(values) / len(values)


def _range_str(values):
    values = [v for v in values if v is not None]
    if not values:
        return "—"
    return f"{min(values):g}–{max(values):g}"


def render_digest(ledger, week_label, start, end, tz, entries, checkins, warnings, session=None):
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tzname = str(tz)
    lines = []
    if session is not None:
        lines.append(f"# sintr weekly digest — session of {week_label}")
        lines.append("")
        lines.append(f"- session: {WEEKDAY_EN[session.weekday()]} {session:%Y-%m-%d %H:%M} ({tzname})")
        lines.append(f"- range: {start:%Y-%m-%d %H:%M} → {end:%Y-%m-%d %H:%M} ({tzname}) — the 7 days before the report")
        lines.append(f"- report: reports/{week_label}.md, front matter `week: {week_label}`, "
                     f"`session: {session:%Y-%m-%dT%H:%M}`, `range: {start:%Y-%m-%d %H:%M} → {end:%Y-%m-%d %H:%M}`")
    else:
        lines.append(f"# sintr weekly digest — {week_label}")
        lines.append("")
        lines.append(f"- range: {start.date()} → {end.date() - timedelta(days=1)} ({tzname})")
    lines.append(f"- entries: {len(entries)} · check-ins: {len(checkins)}")
    lines.append(f"- generated: {generated}")
    lines.append(f"- ledger: {ledger}")
    lines.append("")
    if not entries and not checkins:
        lines.append("**Empty week** — no entries or check-ins in range. A quiet-week report is valid; do not fabricate content.")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Check-ins")
    lines.append("")
    if checkins:
        lines.append("| date | mood | energy | anxiety | sleep_h | quality | note |")
        lines.append("|---|---|---|---|---|---|---|")
        for c in checkins:
            d = c["ts"].astimezone(tz).strftime("%Y-%m-%d")
            def f(v, suffix=""):
                return "—" if v is None else f"{v:g}{suffix}"
            lines.append(
                f"| {d} | {f(c['mood'])}/5 | {f(c['energy'])}/5 | {f(c['anxiety'])}/5 "
                f"| {f(c['sleep_h'])} | {c['sleep_quality'] or '—'} | {c['note'] or '—'} |"
            )
        lines.append("")
        mood = _avg([c["mood"] for c in checkins])
        energy = _avg([c["energy"] for c in checkins])
        anx = _avg([c["anxiety"] for c in checkins])
        sleep = _avg([c["sleep_h"] for c in checkins])
        lines.append("### Check-in aggregates")
        lines.append("")
        lines.append(f"- days: {len(checkins)}")
        if mood is not None:
            lines.append(f"- mood avg: {mood:.1f} ({_range_str([c['mood'] for c in checkins])})")
        if energy is not None:
            lines.append(f"- energy avg: {energy:.1f} ({_range_str([c['energy'] for c in checkins])})")
        if anx is not None:
            lines.append(f"- anxiety avg: {anx:.1f} ({_range_str([c['anxiety'] for c in checkins])})")
        if sleep is not None:
            lines.append(f"- sleep avg: {sleep:.1f} h ({_range_str([c['sleep_h'] for c in checkins])})")
        lines.append("")
    else:
        lines.append("No check-ins in range.")
        lines.append("")

    lines.append("## Entries")
    lines.append("")
    if entries:
        for e in entries:
            local = fmt_ts_local(e["ts"], tz)
            title = e["title"] or "(untitled)"
            lines.append(f"### {e['id']} — {title} ({local} {tzname})")
            if e["emotions"]:
                lines.append(f"- emotions: {fmt_emotions(e['emotions'])}")
            if e["tags"]:
                lines.append(f"- tags: {', '.join(e['tags'])}")
            if e["situation"]:
                lines.append(f"- situation: {e['situation']}")
            if e["thoughts"]:
                lines.append(f"- thoughts: {e['thoughts']}")
            for k, v in e["extra"].items():
                if v:
                    lines.append(f"- {k}: {v}")
            lines.append("")
    else:
        lines.append("No entries in range.")
        lines.append("")

    # aggregates
    freq = {}
    for e in entries:
        for name, value in e["emotions"]:
            freq.setdefault(name.lower(), {"name": name, "values": []})
            freq[name.lower()]["values"].append(value)
    if freq:
        lines.append("## Emotion frequency")
        lines.append("")
        for item in sorted(freq.values(), key=lambda i: (-len(i["values"]), i["name"])):
            vals = item["values"]
            lines.append(f"- {item['name']}: {len(vals)}x (avg {_avg(vals):.0f}, max {max(vals)})")
        lines.append("")

    tag_freq = {}
    for e in entries:
        for t in e["tags"]:
            tag_freq[t] = tag_freq.get(t, 0) + 1
    if tag_freq:
        lines.append("## Tag frequency")
        lines.append("")
        for t, n in sorted(tag_freq.items(), key=lambda kv: -kv[1]):
            lines.append(f"- {t}: {n}x")
        lines.append("")

    lines.append("## Raw entries")
    lines.append("")
    for e in entries:
        lines.append(e["raw"])
        lines.append("")

    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def build_digest(ledger: Path, week_spec, tz_override: str | None, session=None, now=None):
    cfg = read_config(ledger)
    tzname = tz_override or cfg.get("timezone") or "UTC"
    if ZoneInfo is None:
        raise SystemExit("sintr: zoneinfo unavailable; pass --tz UTC")
    try:
        tz = ZoneInfo(tzname)
    except Exception:
        raise SystemExit(f"sintr: unknown timezone {tzname!r}")

    period = resolve_period(cfg, tz, week=week_spec, session=session, now=now)
    start, end, label = period["start"], period["end"], period["label"]
    entries, e_warn = parse_entries(ledger)
    checkins, c_warn = parse_checkins(ledger)
    entries = [e for e in entries if start <= e["ts"] < end]
    checkins = [c for c in checkins if start <= c["ts"] < end]
    warnings = e_warn + c_warn
    return render_digest(ledger, label, start, end, tz, entries, checkins, warnings, period["session"])


def ledger_tz(cfg: dict, tz_override=None):
    tzname = tz_override or cfg.get("timezone") or "UTC"
    try:
        return ZoneInfo(tzname)
    except Exception:
        raise SystemExit(f"sintr: unknown timezone {tzname!r}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="sintr weekly digest collector")
    ap.add_argument("--ledger", default="~/sintr", help="ledger path (default: ~/sintr)")
    period = ap.add_mutually_exclusive_group()
    period.add_argument("--session", default=None,
                        help="next | last | YYYY-MM-DD | YYYY-MM-DDTHH:MM: the 7 days before that session's report "
                             "(default when config.md has session_day and session_time)")
    period.add_argument("--week", default=None, help="this | last | YYYY-Www: a calendar week, Monday to Sunday")
    period.add_argument("--schedule", action="store_true",
                        help="print when to prepare the report (from config.md) and a cron line, then exit")
    ap.add_argument("--tz", default=None, help="IANA timezone (default: config.md timezone, else UTC)")
    ap.add_argument("--out", default="-", help="output path, or - for stdout (default)")
    args = ap.parse_args(argv)

    ledger = Path(args.ledger).expanduser()
    if not ledger.is_dir():
        print(f"sintr: ledger not found: {ledger}", file=sys.stderr)
        return 2

    if args.schedule:
        cfg = read_config(ledger)
        text, ok = schedule(cfg, ledger_tz(cfg, args.tz))
        print(text)
        return 0 if ok else 2

    digest = build_digest(ledger, args.week, args.tz, session=args.session)

    if args.out in ("-", ""):
        print(digest)
    else:
        out = Path(args.out).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(digest + "\n", encoding="utf-8")
        n_e = digest.count("\n### ")
        print(f"sintr: wrote {out} ({n_e} entries in section)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
