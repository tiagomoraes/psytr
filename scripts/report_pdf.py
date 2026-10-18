#!/usr/bin/env python3
"""sintr — weekly report PDF.

Turns a reviewed weekly report (`reports/YYYY-Www.md`) into the document the
therapist receives: an HTML page set in the sintr design system, rendered to a
PDF by headless Chromium. Why the report is shaped this way:
`skills/sintr/references/report-framework.md`.

- Words come from the report Markdown, the reviewed and auditable source: what
  the owner approved is exactly what is printed, nothing is pulled from the
  ledger behind their back. (The optional appendix, `appendix: true` in the
  front matter, prints the week's shareable entries in full; the owner sees it
  in the preview.)
- Numbers, the day-by-day grid and the sentiment chart come from the
  check-ins, computed here, never typed by the agent. Days without a check-in
  stay empty; nothing is interpolated.
- Every quoted span ("...") must be the person's own words: it is looked up in
  the ledger, and moments linked to an entry (`<!-- entry-... -->`) have their
  emotion scores compared with it. Mismatches are reported as warnings.

Stdlib only. Rendering uses Playwright when it is installed, otherwise a
Chrome/Chromium binary (`--print-to-pdf`). With neither, the HTML is still
written and the script says how to print it.

Exit codes: 0 = PDF written; 2 = usage error or missing report; 3 = report is
still a draft (pass --draft for a marked preview); 4 = no renderer found (HTML
written, PDF not); 5 = --strict and the verbatim check raised warnings.
"""

from __future__ import annotations

import argparse
import base64
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path
from string import Template

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import week_collect as wc  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "report_assets"

# Section order of the template. The person's agenda comes second so it lands
# on page 1 (see report-framework.md).
SECTION_KEYS = ("week", "session", "mood", "moments", "patterns", "helped")
SECTION_HINTS = {
    "week": ("como foi", "how the week", "how was the week", "resumo", "summary"),
    "session": ("sessão", "sessao", "session"),
    "mood": ("humor", "mood"),
    "moments": ("momentos", "moments", "situações", "situations"),
    "patterns": ("repetiu", "padrões", "padroes", "repeated", "patterns", "recurring"),
    "helped": ("ajudou", "helped"),
}
COVER_KEYS = ("week", "session")  # leading sections set on page 1, the letter
MOMENT_KEYS = ("when", "tags", "happened", "context", "thoughts", "felt", "body", "did",
               "evidence_for", "evidence_against", "alternative", "felt_after")

H2_RE = re.compile(r"^##\s+(.*?)\s*(?:<!--\s*([a-z_]+)\s*-->)?\s*$")
H3_RE = re.compile(r"^###\s+(.*?)\s*(?:<!--\s*(entry-[\w-]+)\s*-->)?\s*$")
LIST_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+(.*)$")
QUOTE_RE = re.compile(r"“([^”]+)”|\"([^\"]+)\"")
BELIEF_RE = re.compile(r"\((?:believability|acredito|credibilidade)\s*:?\s*(\d{1,3})\s*%?\)", re.I)
DATE_LEAD_RE = re.compile(r"^(.{1,40}?\d.{0,30}?)\s+[—–-]\s+(.+)$")
SUGGESTED_RE = re.compile(r"\s*\((?:sugest[aã]o do sintr|suggested by sintr)\)\s*\.?\s*$", re.I)
BOOKKEEPING_RE = re.compile(r"^(?:completed|corrected|correction|completad[oa]|corrigid[oa]|correção)\b", re.I)
TRUE_WORDS = ("true", "yes", "sim", "1")

STRINGS = {
    "pt": {
        "doc": "Relatório semanal",
        "title_b": "A semana de {name}, nas próprias palavras.",
        "title_b_anon": "A semana, nas próprias palavras.",
        "confidential": "Confidencial",
        "for": "para {therapist}",
        "facts_week": "Semana",
        "facts_checkins": "Check-ins",
        "facts_moments": "Momentos registrados",
        "facts_session": "Próxima sessão",
        "coverage": "{n} de 7 dias",
        "coverage_missing": "sem check-in: {days}",
        "draft": "Rascunho — ainda não revisado. Não enviar.",
        "sec_mood": "Humor, energia e sono",
        "avg_mood": "Humor médio",
        "avg_energy": "Energia média",
        "avg_anxiety": "Ansiedade média",
        "avg_sleep": "Sono médio",
        "of5": "de 5",
        "per_night": "por noite",
        "n_days": "média de {n} dias",
        "n_day": "1 dia",
        "low_high": "mín. {lo} ({lo_days}) · máx. {hi} ({hi_days})",
        "prev": "semana anterior: {v} ({n} dias)",
        "prev_none": "sem dados na semana anterior",
        "legend_mood": "Humor",
        "legend_anxiety": "Ansiedade",
        "legend_sleep": "Horas de sono",
        "this_week": "esta semana",
        "chart_a": "Humor e ansiedade, de 1 (baixo) a 5 (alto)",
        "chart_b": "Sono, em horas por noite",
        "chart_note": "Últimas {n} semanas, esta em destaque. Dias sem check-in ficam em branco: nada é estimado ou ligado por cima.",
        "chart_alt": "Humor e ansiedade de {start} a {end}, de 1 a 5, e horas de sono por noite.",
        "grid_caption": "A semana dia a dia",
        "row_mood": "Humor",
        "row_energy": "Energia",
        "row_anxiety": "Ansiedade",
        "row_sleep": "Sono",
        "row_quality": "Qualidade do sono",
        "row_peak": "Emoção mais forte",
        "row_entries": "Momentos",
        "quality": {"poor": "ruim", "bad": "ruim", "ruim": "ruim", "ok": "ok", "fair": "ok", "regular": "ok",
                    "good": "boa", "boa": "boa", "great": "ótima", "ótima": "ótima"},
        "day_notes": "Nas palavras do dia",
        "no_checkins": "Nenhum check-in nesta semana.",
        "m_happened": "O que aconteceu",
        "m_context": "Contexto",
        "m_thoughts": "O que passou pela cabeça",
        "m_felt": "O que sentiu",
        "m_body": "No corpo",
        "m_did": "O que fez",
        "m_evidence_for": "O que sustentava o pensamento",
        "m_evidence_against": "O que não sustentava",
        "m_alternative": "Outro jeito de ver",
        "m_felt_after": "Depois",
        "not_recorded": "não registrado",
        "strongest": "o mais forte",
        "of100": "de 100",
        "belief": "acredita {v} de 100",
        "suggested": "sugestão do sintr",
        "appendix_title": "Todos os registros da semana",
        "appendix_intro": "Cada registro como foi escrito, em ordem, sem seleção.",
        "foot_prepared": "Preparado a partir de autorregistros — check-ins e registros estruturados — com a ajuda de um assistente pessoal{reviewed}.",
        "foot_reviewed": ", e revisado por {name} antes do envio",
        "foot_reviewed_anon": ", e revisado antes do envio",
        "foot_observations": "As observações são registros datados, não diagnósticos.",
        "foot_clinical": "Não é uma avaliação clínica.",
        "foot_quotes": "Trechos entre aspas e marcados são as palavras exatas da pessoa, copiadas dos registros.",
        "foot_suggested": "Itens marcados como sugestão do sintr foram propostos pelo assistente e mantidos na revisão.",
        "foot_realtime": "Este relatório não é acompanhado em tempo real e não serve para situações de crise.",
        "running": "sintr · {name} · {week} · {conf}",
        "months": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
                   "agosto", "setembro", "outubro", "novembro", "dezembro"],
        "weekdays": ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"],
        "wd_short": ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"],
    },
    "en": {
        "doc": "Weekly report",
        "title_b": "{name}'s week, in their own words.",
        "title_b_anon": "The week, in their own words.",
        "confidential": "Confidential",
        "for": "for {therapist}",
        "facts_week": "Week",
        "facts_checkins": "Check-ins",
        "facts_moments": "Moments recorded",
        "facts_session": "Next session",
        "coverage": "{n} of 7 days",
        "coverage_missing": "none on {days}",
        "draft": "Draft — not reviewed yet. Do not send.",
        "sec_mood": "Mood, energy and sleep",
        "avg_mood": "Average mood",
        "avg_energy": "Average energy",
        "avg_anxiety": "Average anxiety",
        "avg_sleep": "Average sleep",
        "of5": "of 5",
        "per_night": "a night",
        "n_days": "average of {n} days",
        "n_day": "1 day",
        "low_high": "low {lo} ({lo_days}) · high {hi} ({hi_days})",
        "prev": "week before: {v} ({n} days)",
        "prev_none": "no data the week before",
        "legend_mood": "Mood",
        "legend_anxiety": "Anxiety",
        "legend_sleep": "Hours of sleep",
        "this_week": "this week",
        "chart_a": "Mood and anxiety, from 1 (low) to 5 (high)",
        "chart_b": "Sleep, in hours a night",
        "chart_note": "Last {n} weeks, this one highlighted. Days without a check-in stay blank: nothing is estimated or drawn across.",
        "chart_alt": "Mood and anxiety from {start} to {end}, 1 to 5, and hours of sleep per night.",
        "grid_caption": "The week day by day",
        "row_mood": "Mood",
        "row_energy": "Energy",
        "row_anxiety": "Anxiety",
        "row_sleep": "Sleep",
        "row_quality": "Sleep quality",
        "row_peak": "Strongest emotion",
        "row_entries": "Moments",
        "quality": {"poor": "poor", "bad": "poor", "ok": "ok", "fair": "ok", "good": "good", "great": "great"},
        "day_notes": "In the day's own words",
        "no_checkins": "No check-ins this week.",
        "m_happened": "What happened",
        "m_context": "Context",
        "m_thoughts": "What went through their mind",
        "m_felt": "What they felt",
        "m_body": "In the body",
        "m_did": "What they did",
        "m_evidence_for": "What supported the thought",
        "m_evidence_against": "What didn't",
        "m_alternative": "Another way to see it",
        "m_felt_after": "Afterwards",
        "not_recorded": "not recorded",
        "strongest": "the strongest",
        "of100": "of 100",
        "belief": "believes it {v} of 100",
        "suggested": "suggested by sintr",
        "appendix_title": "Every entry this week",
        "appendix_intro": "Each entry as it was written, in order, unselected.",
        "foot_prepared": "Prepared from self-reports — check-ins and structured entries — with the help of a personal assistant{reviewed}.",
        "foot_reviewed": ", and reviewed by {name} before sending",
        "foot_reviewed_anon": ", and reviewed before sending",
        "foot_observations": "Observations are dated records, not diagnoses.",
        "foot_clinical": "Not a clinical assessment.",
        "foot_quotes": "Highlighted words in quotes are the person's exact words, copied from their records.",
        "foot_suggested": "Items marked as suggested by sintr were proposed by the assistant and kept during review.",
        "foot_realtime": "This report is not monitored in real time and is not a crisis channel.",
        "running": "sintr · {name} · {week} · {conf}",
        "months": ["January", "February", "March", "April", "May", "June", "July",
                   "August", "September", "October", "November", "December"],
        "weekdays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "wd_short": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
}

WEEKDAY_NAMES = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
    "segunda": 0, "terça": 1, "terca": 1, "quarta": 2, "quinta": 3, "sexta": 4, "sábado": 5, "sabado": 5,
    "domingo": 6,
}

# Chart colors: the two ends of the brand glyph's window light (sky, peach),
# deepened until they work as 2px lines on paper. Validated as a categorical
# pair (lightness band, chroma floor, CVD separation, contrast >= 3:1).
MOOD_COLOR = "#3a6ea5"
ANXIETY_COLOR = "#c4744a"
SLEEP_COLOR = "#7d917a"       # leaf-shadow sage, deepened
SLEEP_COLOR_PAST = "#d3dccf"
LIGHT_STOPS = ("#d4e6f4", "#f1e8df", "#f8dcc8")  # morning window light
LEAF = "#a9b9a3"


class ReportError(Exception):
    """A problem the owner or agent must fix before a PDF can be made."""

    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------
# language, numbers and dates
# --------------------------------------------------------------------------

def lang_of(raw: str) -> str:
    raw = (raw or "").strip().lower()
    return "pt" if raw.startswith("pt") or "portug" in raw else "en"


def fmt_num(value: float, lang: str, digits: int = 1) -> str:
    text = f"{value:.{digits}f}"
    return text.replace(".", ",") if lang == "pt" else text


def fmt_score(value: float, lang: str) -> str:
    """Check-in scores: integers stay integers (4), halves keep one digit (3,5)."""
    return str(int(value)) if float(value).is_integer() else fmt_num(value, lang)


def fmt_hours(hours: float) -> str:
    minutes = int(round(hours * 60 / 5.0)) * 5
    h, m = divmod(minutes, 60)
    return f"{h}h{m:02d}" if m else f"{h}h"


def fmt_day_month(d: date, lang: str) -> str:
    return f"{d.day}/{d.month}" if lang == "pt" else f"{d.month}/{d.day}"


def fmt_range(start: date, end: date, lang: str) -> str:
    months = STRINGS[lang]["months"]
    if lang == "pt":
        if start.year != end.year:
            return f"{start.day} de {months[start.month - 1]} de {start.year} a {end.day} de {months[end.month - 1]} de {end.year}"
        if start.month != end.month:
            return f"{start.day} de {months[start.month - 1]} a {end.day} de {months[end.month - 1]}"
        return f"{start.day} a {end.day} de {months[end.month - 1]}"
    if start.year != end.year:
        return f"{months[start.month - 1]} {start.day}, {start.year} – {months[end.month - 1]} {end.day}, {end.year}"
    if start.month != end.month:
        return f"{months[start.month - 1]} {start.day} – {months[end.month - 1]} {end.day}"
    return f"{months[start.month - 1]} {start.day}–{end.day}"


def fmt_when(dt: datetime, lang: str) -> str:
    s = STRINGS[lang]
    weekday = s["weekdays"][dt.weekday()]
    month = s["months"][dt.month - 1]
    if lang == "pt":
        clock = f"{dt.hour}h{dt.minute:02d}" if dt.minute else f"{dt.hour}h"
        return f"{weekday}, {dt.day} de {month} · {clock}"
    return f"{weekday}, {month} {dt.day} · {dt.hour:02d}:{dt.minute:02d}"


def fmt_weekdays(days, lang: str) -> str:
    return ", ".join(STRINGS[lang]["wd_short"][d.weekday()] for d in days)


def next_session(week_end: date, cfg: dict, lang: str):
    """The first configured session day after the reported week, or None."""
    raw = (cfg.get("session_day") or "").strip().lower()
    day = WEEKDAY_NAMES.get(raw.split()[0].rstrip(",")) if raw else None
    if day is None:
        return None
    d = week_end + timedelta(days=1)
    while d.weekday() != day:
        d += timedelta(days=1)
    s = STRINGS[lang]
    text = f"{s['weekdays'][d.weekday()]}, {fmt_day_month(d, lang)}"
    clock = (cfg.get("session_time") or "").strip()
    m = re.match(r"^(\d{1,2}):(\d{2})$", clock)
    if m:
        hh, mm = int(m.group(1)), int(m.group(2))
        if lang == "pt":
            text += f", {hh}h{mm:02d}" if mm else f", {hh}h"
        else:
            text += f", {hh:02d}:{mm:02d}"
    return text


# --------------------------------------------------------------------------
# the report Markdown
# --------------------------------------------------------------------------

def parse_front_matter(text: str):
    meta, body = {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, flags=re.S)
    if m:
        for line in m.group(1).splitlines():
            line = re.sub(r"\s+#.*$", "", line)
            km = re.match(r"^([a-z_]+)\s*:\s*(.*)$", line.strip())
            if km:
                meta[km.group(1)] = km.group(2).strip()
        body = m.group(2)
    return meta, body


def section_key(heading: str, marker: str | None):
    if marker in SECTION_KEYS:
        return marker
    low = heading.lower()
    for key in SECTION_KEYS:
        if any(h in low for h in SECTION_HINTS[key]):
            return key
    return None


def drop_comments(body: str) -> str:
    """Remove HTML comments (template notes for the agent), keeping the ones
    on heading lines: those are section and entry markers."""
    def keep_markers(m):
        line_start = body.rfind("\n", 0, m.start()) + 1
        return m.group(0) if body[line_start:m.start()].lstrip().startswith("#") else ""
    return wc.COMMENT_RE.sub(keep_markers, body)


def parse_report(text: str) -> dict:
    """Split a report into front matter, title and ordered H2 sections. The
    disclaimer line under the last `---` is dropped: the PDF prints its own."""
    meta, body = parse_front_matter(text)
    body = drop_comments(body)
    title, sections, current = "", [], None
    for line in body.splitlines():
        if line.startswith("# ") and not title and current is None:
            title = line[2:].strip()
            continue
        m = H2_RE.match(line)
        if m:
            current = {"heading": m.group(1).strip(), "key": section_key(m.group(1), m.group(2)), "lines": []}
            sections.append(current)
            continue
        if current is not None:
            current["lines"].append(line)
    if sections:
        last = sections[-1]["lines"]
        for i, line in enumerate(last):
            if line.strip() == "---":
                del last[i:]
                break
    return {"meta": meta, "title": title, "sections": sections}


def blocks(lines):
    """Group Markdown lines into ('p', text) and ('ul', [items]) blocks."""
    out, para, items = [], [], None
    def flush_para():
        if para:
            out.append(("p", " ".join(s.strip() for s in para)))
            para.clear()
    for line in lines:
        if not line.strip():
            flush_para()
            items = None
            continue
        m = LIST_RE.match(line)
        if m:
            flush_para()
            if items is None:
                items = []
                out.append(("ul", items))
            items.append(m.group(1).strip())
        elif items is not None and line.startswith((" ", "\t")):
            items[-1] = items[-1] + " " + line.strip()
        else:
            items = None
            para.append(line)
    flush_para()
    return out


def parse_moments(lines):
    """`### Title <!-- entry-id -->` blocks with `- key: value` fields."""
    intro, moments, current = [], [], None
    for line in lines:
        m = H3_RE.match(line)
        if m:
            current = {"title": m.group(1).strip(), "entry_id": m.group(2), "fields": {}, "rest": []}
            moments.append(current)
            continue
        if current is None:
            intro.append(line)
            continue
        fm = wc.FIELD_RE.match(line)
        if fm and fm.group(1) in MOMENT_KEYS:
            current["fields"][fm.group(1)] = fm.group(2).strip()
            current["_last"] = fm.group(1)
        elif line.strip() and current.get("_last") and line.startswith((" ", "\t")):
            key = current["_last"]
            current["fields"][key] = current["fields"][key] + " " + line.strip()
        elif line.strip():
            current["rest"].append(line)
    for mo in moments:
        mo.pop("_last", None)
    return intro, moments


# --------------------------------------------------------------------------
# inline Markdown -> HTML
# --------------------------------------------------------------------------

def _emphasis(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    return text


def inline(text: str) -> str:
    """Escape, set emphasis, and put the person's quoted words under the
    verbatim highlighter (<q class="said">)."""
    out, pos = [], 0
    for m in QUOTE_RE.finditer(text):
        out.append(_emphasis(text[pos:m.start()]))
        out.append(f'<q class="said">{html.escape(m.group(1) or m.group(2), quote=False)}</q>')
        pos = m.end()
    out.append(_emphasis(text[pos:]))
    return "".join(out)


def quotes_in(text: str):
    return [m.group(1) or m.group(2) for m in QUOTE_RE.finditer(text or "")]


# --------------------------------------------------------------------------
# verbatim check
# --------------------------------------------------------------------------

def _norm(text: str) -> str:
    text = (text or "").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().casefold()


def shareable(entry) -> bool:
    return entry["extra"].get("share", "").strip().lower() != "no"


def ledger_corpus(ledger: Path, entries):
    """What a report may quote — shareable entries, check-in notes, therapy
    notes — and, apart, the text of entries marked `share: no`."""
    parts = [e["raw"] for e in entries if shareable(e)]
    for sub in ("checkins", "therapy", "therapy/sessions"):
        for path in sorted((ledger / sub).glob("*.md")):
            if path.name.startswith("YYYY"):
                continue
            parts.append(wc.strip_comments(path.read_text(encoding="utf-8")))
    private = [e["raw"] for e in entries if not shareable(e)]
    return _norm("\n".join(parts)), _norm("\n".join(private))


def verbatim_warnings(report: dict, entries_by_id: dict, corpus: str, private: str = ""):
    warnings = []
    for sec in report["sections"]:
        for line in sec["lines"]:
            for q in quotes_in(line):
                needle = _norm(q).strip(" .,;:!?…")
                if not needle or needle in corpus:
                    continue
                if needle in private:
                    warnings.append(f"“{q}” ({sec['heading']}): comes from an entry marked share: no — remove it")
                else:
                    warnings.append(f"“{q}” ({sec['heading']}): not found in the ledger — quotes must be the person's exact words")
        if sec["key"] != "moments":
            continue
        _, moments = parse_moments(sec["lines"])
        for mo in moments:
            eid = mo["entry_id"]
            if not eid:
                continue
            entry = entries_by_id.get(eid)
            if entry is None:
                warnings.append(f"moment {mo['title']!r}: {eid} not found in the ledger")
                continue
            if not shareable(entry):
                warnings.append(f"moment {mo['title']!r}: {eid} is marked share: no — remove it")
            for field, source in (("felt", entry["emotions"]),
                                  ("felt_after", wc.parse_emotions(entry["extra"].get("emotions_after", ""))[0])):
                said, _ = wc.parse_emotions(mo["fields"].get(field, ""))
                recorded = {name.casefold(): value for name, value in source}
                for name, value in said:
                    if name.casefold() not in recorded:
                        warnings.append(f"moment {mo['title']!r}: emotion {name!r} is not in {eid}")
                    elif recorded[name.casefold()] != value:
                        warnings.append(f"moment {mo['title']!r}: {name} {value} but {eid} records {recorded[name.casefold()]}")
    return warnings


# --------------------------------------------------------------------------
# check-in series
# --------------------------------------------------------------------------

def daily_series(checkins, tz, first: date, last: date):
    """One record per local day in [first, last]; a missing day keeps None."""
    by_day = {}
    for c in checkins:
        by_day[c["ts"].astimezone(tz).date()] = c  # one check-in per day; last wins
    days, d = [], first
    while d <= last:
        c = by_day.get(d, {})
        days.append({"date": d, **{k: c.get(k) for k in ("mood", "energy", "anxiety", "sleep_h")},
                     "sleep_quality": (c.get("sleep_quality") or "").strip() or None})
        d += timedelta(days=1)
    return days


def logged(day) -> bool:
    return any(day[k] is not None for k in ("mood", "energy", "anxiety", "sleep_h"))


def avg(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


# --------------------------------------------------------------------------
# SVG: the sentiment chart
# --------------------------------------------------------------------------

def _f(v: float) -> str:
    """Deterministic coordinates: two decimals, no trailing zeros."""
    text = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def _polylines(points, in_week):
    """Split (x, y|None) points into runs of consecutive days, each run cut
    into the part before the highlighted week and the part inside it."""
    past, now = [], []
    for i in range(len(points) - 1):
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        if y0 is None or y1 is None:
            continue
        (now if in_week[i] else past).append(((x0, y0), (x1, y1)))
    def join(segments):
        paths, run = [], []
        for a, b in segments:
            if run and run[-1] == a:
                run.append(b)
            else:
                if run:
                    paths.append(run)
                run = [a, b]
        if run:
            paths.append(run)
        return ["M" + " L".join(f"{_f(x)} {_f(y)}" for x, y in run) for run in paths]
    return join(past), join(now)


def sentiment_chart(days, week_start: date, lang: str):
    """Two small multiples on one day axis (never a dual axis): mood and
    anxiety on their shared 1–5 scale, then sleep hours as bars."""
    s = STRINGS[lang]
    n = len(days)
    W, left, right = 660.0, 30.0, 6.0
    slot = (W - left - right) / n
    xs = [left + slot * (i + 0.5) for i in range(n)]
    in_week = [d["date"] >= week_start for d in days]
    w0 = in_week.index(True) if True in in_week else n
    band_x, band_w = left + slot * w0, slot * (n - w0)

    # Panel A: mood and anxiety, 1-5.
    top, h = 22.0, 120.0
    def ya(v):
        return top + (5 - v) / 4 * h
    alt = s["chart_alt"].format(start=fmt_day_month(days[0]["date"], lang), end=fmt_day_month(days[-1]["date"], lang))
    a = [f'<svg class="chart__svg" viewBox="0 0 {_f(W)} {_f(top + h + 12)}" role="img" aria-label="{html.escape(alt)}">']
    a.append('<defs><linearGradient id="wk-light" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{LIGHT_STOPS[0]}"/><stop offset=".55" stop-color="{LIGHT_STOPS[1]}"/>'
             f'<stop offset="1" stop-color="{LIGHT_STOPS[2]}"/></linearGradient></defs>')
    if w0 < n:
        a.append(f'<rect class="chart__band" x="{_f(band_x)}" y="0" width="{_f(band_w)}" height="{_f(top + h + 12)}" rx="8" fill="url(#wk-light)"/>')
        a.append(f'<text class="chart__band-label" x="{_f(band_x + 8)}" y="13">{html.escape(s["this_week"])}</text>')
    for v in (1, 2, 3, 4, 5):
        y = ya(v)
        a.append(f'<line class="chart__grid" x1="{_f(left)}" x2="{_f(W - right)}" y1="{_f(y)}" y2="{_f(y)}"/>')
        if v in (1, 3, 5):
            a.append(f'<text class="chart__tick" x="{_f(left - 10)}" y="{_f(y + 3.5)}" text-anchor="end">{v}</text>')
    for key, color in (("mood", MOOD_COLOR), ("anxiety", ANXIETY_COLOR)):
        pts = [(xs[i], ya(d[key]) if d[key] is not None else None) for i, d in enumerate(days)]
        past, now = _polylines(pts, in_week)
        for path in past:
            a.append(f'<path class="chart__line chart__line--past chart__line--{key}" d="{path}" stroke="{color}"/>')
        for path in now:
            a.append(f'<path class="chart__line chart__line--{key}" d="{path}" stroke="{color}"/>')
        for i, (x, y) in enumerate(pts):
            if y is None:
                continue
            lonely = (i == 0 or pts[i - 1][1] is None) and (i == n - 1 or pts[i + 1][1] is None)
            if not in_week[i]:
                if lonely:
                    a.append(f'<circle class="chart__dot--past" cx="{_f(x)}" cy="{_f(y)}" r="2.5" fill="{color}"/>')
                continue
            if key == "mood":
                a.append(f'<circle class="chart__dot" cx="{_f(x)}" cy="{_f(y)}" r="4" fill="{color}"/>')
            elif days[i]["mood"] is not None and days[i]["mood"] == days[i]["anxiety"]:
                # same value as mood: a ring around the mood dot, both stay visible
                a.append(f'<circle class="chart__ring" cx="{_f(x)}" cy="{_f(y)}" r="7" stroke="{color}"/>')
            else:
                a.append(f'<circle class="chart__hollow" cx="{_f(x)}" cy="{_f(y)}" r="3.6" stroke="{color}"/>')
    a.append("</svg>")

    # Panel B: sleep hours, bars from one baseline.
    peak = max([d["sleep_h"] for d in days if d["sleep_h"] is not None] + [9.0])
    hi = float(int(peak) + (0 if float(peak).is_integer() else 1))
    btop, bh, axis = 6.0, 54.0, 30.0
    base = btop + bh
    def yb(v):
        return base - v / hi * bh
    b = [f'<svg class="chart__svg" viewBox="0 0 {_f(W)} {_f(base + axis)}" aria-hidden="true">']
    if w0 < n:
        b.append(f'<rect class="chart__band" x="{_f(band_x)}" y="0" width="{_f(band_w)}" height="{_f(base + 4)}" rx="8" fill="url(#wk-light)"/>')
    for v in (4, 8):
        if v <= hi:
            b.append(f'<line class="chart__grid" x1="{_f(left)}" x2="{_f(W - right)}" y1="{_f(yb(v))}" y2="{_f(yb(v))}"/>')
            b.append(f'<text class="chart__tick" x="{_f(left - 10)}" y="{_f(yb(v) + 3.5)}" text-anchor="end">{v}h</text>')
    b.append(f'<line class="chart__base" x1="{_f(left)}" x2="{_f(W - right)}" y1="{_f(base)}" y2="{_f(base)}"/>')
    bw = min(14.0, slot * 0.5)
    for i, d in enumerate(days):
        v = d["sleep_h"]
        if v is None or v <= 0:
            continue
        x0, y0 = xs[i] - bw / 2, yb(v)
        r = min(3.0, bw / 2, base - y0)
        fill = SLEEP_COLOR if in_week[i] else SLEEP_COLOR_PAST
        b.append(f'<path d="M{_f(x0)} {_f(base)} V{_f(y0 + r)} Q{_f(x0)} {_f(y0)} {_f(x0 + r)} {_f(y0)} '
                 f'H{_f(x0 + bw - r)} Q{_f(x0 + bw)} {_f(y0)} {_f(x0 + bw)} {_f(y0 + r)} V{_f(base)} Z" fill="{fill}"/>')
    # x axis: every day of the highlighted week, the first day of earlier weeks
    for i, d in enumerate(days):
        x = xs[i]
        if in_week[i]:
            b.append(f'<text class="chart__day" x="{_f(x)}" y="{_f(base + 13)}" text-anchor="middle">{html.escape(s["wd_short"][d["date"].weekday()])}</text>')
            b.append(f'<text class="chart__date" x="{_f(x)}" y="{_f(base + 25)}" text-anchor="middle">{d["date"].day}</text>')
        elif d["date"].weekday() == 0 or i == 0:
            b.append(f'<text class="chart__date" x="{_f(x)}" y="{_f(base + 13)}" text-anchor="middle">{fmt_day_month(d["date"], lang)}</text>')
    b.append("</svg>")
    return "\n".join(a), "\n".join(b)


# --------------------------------------------------------------------------
# HTML pieces
# --------------------------------------------------------------------------

GLYPH = ('<svg class="mark__glyph" viewBox="0 0 32 32" aria-hidden="true"><defs>'
         '<linearGradient id="mark-grad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#cfe3f3"/>'
         '<stop offset=".55" stop-color="#f6e1d3"/><stop offset="1" stop-color="#f7cfb5"/></linearGradient></defs>'
         '<rect width="32" height="32" rx="8" fill="#16171a"/><g fill="url(#mark-grad)" transform="translate(10.4 6.2) skewX(-14)">'
         '<rect x="0" y="0" width="6" height="8.8" rx="1"/><rect x="7.2" y="0" width="6" height="8.8" rx="1"/>'
         '<rect x="0" y="10.2" width="6" height="8.8" rx="1"/><rect x="7.2" y="10.2" width="6" height="8.8" rx="1"/></g></svg>')

# The window light of the site, held in the header of the first page: a tall
# window projected obliquely onto the paper, with sage leaf shadows. Shapes
# from site/index.html; static (no time of day, no motion).
LIGHT = f"""<svg class="light__svg" viewBox="0 0 1000 1000" aria-hidden="true">
<defs>
<linearGradient id="light-grad" x1="0" y1="0" x2="1" y2="1">
<stop offset=".18" stop-color="{LIGHT_STOPS[0]}"/><stop offset=".5" stop-color="{LIGHT_STOPS[1]}"/><stop offset=".82" stop-color="{LIGHT_STOPS[2]}"/>
</linearGradient>
<filter id="light-edge" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="11"/></filter>
<filter id="light-leaf" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3.4"/></filter>
<mask id="light-window" maskUnits="userSpaceOnUse" x="-500" y="-500" width="2000" height="2000">
<g filter="url(#light-edge)" fill="#fff" transform="translate(430 110) skewX(-15) skewY(8)">
<rect x="0" y="0" width="150" height="188" rx="3"/><rect x="166" y="0" width="150" height="188" rx="3"/>
<rect x="0" y="204" width="150" height="188" rx="3"/><rect x="166" y="204" width="150" height="188" rx="3"/>
<rect x="0" y="408" width="150" height="188" rx="3"/><rect x="166" y="408" width="150" height="188" rx="3"/>
</g>
</mask>
</defs>
<g mask="url(#light-window)">
<rect x="200" y="60" width="600" height="840" fill="url(#light-grad)"/>
<g filter="url(#light-leaf)" fill="{LEAF}" opacity=".62">
<path fill="none" stroke="{LEAF}" stroke-width="3.5" stroke-linecap="round" d="M960 60 C 870 120, 800 170, 700 250 S 560 380, 500 470"/>
<path d="M900 104c-26-30-68-34-92-16 25 27 62 34 92 16z"/><path d="M866 128c9-39-10-76-39-87-7 36 9 71 39 87z"/>
<path d="M816 164c-32-23-74-20-94 4 28 19 67 21 94-4z"/><path d="M786 186c14-37 2-78-25-92-12 34-2 73 25 92z"/>
<path d="M733 225c-35-16-76-5-90 21 32 12 71 5 90-21z"/><path d="M701 250c19-34 16-76-7-94-18 30-16 69 7 94z"/>
<path d="M651 291c-35-11-74 5-85 34 34 7 69-5 85-34z"/><path d="M618 321c25-30 28-73 7-94-21 27-25 66-7 94z"/>
<path d="M575 362c-37-5-73 16-80 46 34 2 67-16 80-46z"/><path d="M545 398c27-27 35-67 18-92-23 23-32 62-18 92z"/>
<path d="M515 442c-35 2-65 28-67 58 34-5 62-28 67-58z"/>
</g>
</g>
</svg>"""


ARROW = ('<svg class="arrow" viewBox="0 0 12 8" aria-hidden="true">'
         '<path d="M1 4h9.2M7.2 1.2 10 4 7.2 6.8"/></svg>')


def render_blocks(lines, cls="") -> str:
    out = []
    for kind, value in blocks(lines):
        if kind == "p":
            out.append(f'<p{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{inline(value)}</p>')
        else:
            out.append('<ul class="dash">' + "".join(f"<li>{inline(i)}</li>" for i in value) + "</ul>")
    return "\n".join(out)


def render_dated(items, cls="obs") -> str:
    """List items that open with their dates (`13 e 15/10 — ...`): the dates
    get their own column."""
    rows = []
    for item in items:
        m = DATE_LEAD_RE.match(item)
        if m and not QUOTE_RE.search(m.group(1)):
            rows.append(f'<li><span class="obs__when">{inline(m.group(1))}</span><span class="obs__what">{inline(m.group(2))}</span></li>')
        else:
            rows.append(f'<li><span class="obs__what obs__what--wide">{inline(item)}</span></li>')
    return f'<ul class="{cls}">' + "".join(rows) + "</ul>"


def render_observations(lines) -> str:
    return "\n".join(f"<p>{inline(v)}</p>" if kind == "p" else render_dated(v) for kind, v in blocks(lines))


def render_topics(lines, lang: str):
    """The agenda as an open checklist. Returns (html, has_suggestions)."""
    out, suggested = [], False
    for kind, value in blocks(lines):
        if kind == "p":
            out.append(f"<p>{inline(value)}</p>")
            continue
        items = []
        for item in value:
            tag = ""
            if SUGGESTED_RE.search(item):
                item, suggested = SUGGESTED_RE.sub("", item), True
                tag = f' <span class="scale scale--tag">{html.escape(STRINGS[lang]["suggested"])}</span>'
            items.append(f'<li><span class="tick" aria-hidden="true"></span><span>{inline(item)}{tag}</span></li>')
        out.append('<ul class="topics">' + "".join(items) + "</ul>")
    return "\n".join(out), suggested


def render_feelings(raw: str, lang: str, before=None) -> str:
    """Emotion chips with their 0–100 intensity; with `before`, a re-rate
    shows as `70 → 45`."""
    emotions, _ = wc.parse_emotions(raw)
    if not emotions:
        return inline(raw)
    s, before = STRINGS[lang], {k.casefold(): v for k, v in (before or [])}
    chips = []
    for name, value in emotions:
        was = before.get(name.casefold())
        # the arrow is drawn: U+2192 is not in the embedded Latin subsets
        scale = (f"{was} {ARROW} {value}" if was is not None else f"{value} {s['of100']}")
        chips.append(f'<span class="feel__item">{html.escape(name)}<span class="scale">{scale}</span></span>')
    return '<span class="feel">' + "".join(chips) + "</span>"


def render_thoughts(raw: str, lang: str, strongest=None) -> str:
    quotes = quotes_in(raw)
    if not quotes:
        return inline(raw)
    out = []
    for q in quotes:
        mark = ""
        if strongest and _norm(q) in strongest:
            mark = f' <span class="scale scale--tag">{html.escape(STRINGS[lang]["strongest"])}</span>'
        out.append(f'<span class="thought"><q class="said">{html.escape(q, quote=False)}</q>{mark}</span>')
    return "".join(out)


def render_alternative(raw: str, lang: str) -> str:
    m = BELIEF_RE.search(raw)
    out = render_thoughts(BELIEF_RE.sub("", raw).strip(), lang)
    if m:
        out += f'<span class="scale scale--after">{html.escape(STRINGS[lang]["belief"].format(v=m.group(1)))}</span>'
    return out


def render_moment(mo: dict, entry, tz, lang: str, compact: bool = False) -> str:
    """A notebook card. Emotions lead under the title, for scanning; the rows
    follow the thought record: situation, thoughts, body, action, then the
    working stage when the person did it."""
    s, f = STRINGS[lang], mo["fields"]
    missing = f'<span class="none">{s["not_recorded"]}</span>'
    when = f.get("when") or (fmt_when(entry["ts"].astimezone(tz), lang) if entry else "")
    head = f'<div class="note__head"><span class="note__when">{inline(when)}</span>'
    if f.get("tags"):
        head += f'<span class="note__tag">{html.escape(f["tags"])}</span>'
    head += "</div>"
    feel = f'<p class="note__feel">{render_feelings(f["felt"], lang)}</p>' if f.get("felt") else ""
    strongest = {_norm(q) for q in quotes_in(entry["extra"].get("hot_thought", ""))} if entry else set()
    rows = []
    def row(label, value_html):
        rows.append(f'<div class="note__row"><dt>{html.escape(label)}</dt><dd>{value_html}</dd></div>')
    row(s["m_happened"], inline(f["happened"]) if f.get("happened") else missing)
    if f.get("context"):
        row(s["m_context"], inline(f["context"]))
    row(s["m_thoughts"], render_thoughts(f["thoughts"], lang, strongest) if f.get("thoughts") else missing)
    if not f.get("felt"):
        row(s["m_felt"], missing)
    if f.get("body"):
        row(s["m_body"], inline(f["body"]))
    row(s["m_did"], inline(f["did"]) if f.get("did") else missing)
    if f.get("evidence_for"):
        row(s["m_evidence_for"], inline(f["evidence_for"]))
    if f.get("evidence_against"):
        row(s["m_evidence_against"], inline(f["evidence_against"]))
    if f.get("alternative"):
        row(s["m_alternative"], render_alternative(f["alternative"], lang))
    if f.get("felt_after"):
        row(s["m_felt_after"], render_feelings(f["felt_after"], lang, wc.parse_emotions(f.get("felt", ""))[0]))
    rest = render_blocks(mo["rest"], "note__para") if mo["rest"] else ""
    cls = "note note--compact" if compact else "note"
    return (f'<article class="{cls}">{head}<h3 class="note__title">{inline(mo["title"])}</h3>{feel}'
            f'<dl class="note__rows">{"".join(rows)}</dl>{rest}</article>')


def entry_as_moment(entry) -> dict:
    """A ledger entry in the moment shape, for the appendix."""
    x = entry["extra"]
    fields = {
        "tags": ", ".join(entry["tags"]),
        "happened": entry["situation"],
        "context": entry["context"],
        "thoughts": entry["thoughts"],
        "felt": " ; ".join(f"{n} {v}" for n, v in entry["emotions"]),
        "body": entry["body"],
        "did": entry["behavior"],
        "evidence_for": x.get("evidence_for", ""),
        "evidence_against": x.get("evidence_against", ""),
        "alternative": x.get("alternative", ""),
        "felt_after": x.get("emotions_after", ""),
    }
    fields = {k: v for k, v in fields.items() if v and v.strip().lower() != "unknown"}
    # notes keep the person's words; the agent's bookkeeping ("completed …") stays in the ledger
    notes = [n.strip() for n in entry["notes"].split(" ; ") if n.strip() and not BOOKKEEPING_RE.match(n.strip())]
    return {"title": entry["title"] or entry["id"], "entry_id": entry["id"], "fields": fields,
            "rest": [" ; ".join(notes)] if notes else []}


def render_stats(week_days, prev_days, lang: str) -> str:
    s = STRINGS[lang]
    cells = []
    for key, label in (("mood", "avg_mood"), ("energy", "avg_energy"), ("anxiety", "avg_anxiety"), ("sleep_h", "avg_sleep")):
        days = [d for d in week_days if d[key] is not None]
        if not days:
            continue
        vals = [d[key] for d in days]
        value = sum(vals) / len(vals)
        prev_vals = [d[key] for d in prev_days if d[key] is not None]
        fmt = fmt_hours if key == "sleep_h" else (lambda v: fmt_score(v, lang))
        if key == "sleep_h":
            main = f'{fmt_hours(value)}<span class="stat__unit">{s["per_night"]}</span>'
            prev_txt = fmt_hours(avg(prev_vals)) if prev_vals else None
        else:
            main = f'{fmt_num(value, lang)}<span class="stat__unit">{s["of5"]}</span>'
            prev_txt = fmt_num(avg(prev_vals), lang) if prev_vals else None
        sub = [s["n_days"].format(n=len(vals)) if len(vals) > 1 else s["n_day"]]
        lo, hi = min(vals), max(vals)
        if lo != hi:
            sub.append(s["low_high"].format(
                lo=fmt(lo), lo_days=fmt_weekdays([d["date"] for d in days if d[key] == lo], lang),
                hi=fmt(hi), hi_days=fmt_weekdays([d["date"] for d in days if d[key] == hi], lang)))
        sub.append(s["prev"].format(v=prev_txt, n=len(prev_vals)) if prev_txt else s["prev_none"])
        cells.append(f'<div class="stat"><dt>{s[label]}</dt><dd class="stat__value">{main}</dd>'
                     + "".join(f'<dd class="stat__sub">{x}</dd>' for x in sub) + "</div>")
    return '<dl class="stats">' + "".join(cells) + "</dl>"


def render_grid(week_days, week_entries, tz, lang: str) -> str:
    """The diary-card view: one column per day, one row per measure, every
    cell the day's check-in value (or a dash), plus the day's moments."""
    s = STRINGS[lang]
    per_day = {}
    for e in week_entries:
        per_day.setdefault(e["ts"].astimezone(tz).date(), []).append(e)
    head = "".join(
        f'<th scope="col"><span class="days__wd">{html.escape(s["wd_short"][d["date"].weekday()])}</span>'
        f'<span class="days__d">{fmt_day_month(d["date"], lang)}</span></th>' for d in week_days)
    none = '<td class="days__none">—</td>'
    rows = []
    for key, label in (("mood", "row_mood"), ("energy", "row_energy"), ("anxiety", "row_anxiety"), ("sleep_h", "row_sleep")):
        cells = [none if d[key] is None else f"<td>{fmt_hours(d[key]) if key == 'sleep_h' else fmt_score(d[key], lang)}</td>"
                 for d in week_days]
        rows.append(f'<tr><th scope="row">{s[label]}</th>{"".join(cells)}</tr>')
    if any(d["sleep_quality"] for d in week_days):
        cells = [f'<td class="days__word">{html.escape(s["quality"].get(d["sleep_quality"].lower(), d["sleep_quality"]))}</td>'
                 if d["sleep_quality"] else none for d in week_days]
        rows.append(f'<tr><th scope="row">{s["row_quality"]}</th>{"".join(cells)}</tr>')
    peaks, marks = [], []
    for d in week_days:
        day_entries = per_day.get(d["date"], [])
        values = [v for e in day_entries for _, v in e["emotions"]]
        peaks.append(f"<td>{max(values)}</td>" if values else none)
        marks.append(f'<td class="days__marks">{"".join("<i></i>" for _ in day_entries)}</td>' if day_entries else none)
    rows.append(f'<tr><th scope="row">{s["row_peak"]} <span class="days__unit">0–100</span></th>{"".join(peaks)}</tr>')
    rows.append(f'<tr><th scope="row">{s["row_entries"]}</th>{"".join(marks)}</tr>')
    return (f'<table class="days"><caption>{s["grid_caption"]}</caption><thead><tr><td></td>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def css_string(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def font_faces() -> str:
    faces = (("Source Serif 4", "source-serif-4-roman.woff2", "200 600", "normal"),
             ("Source Serif 4", "source-serif-4-italic.woff2", "200 600", "italic"),
             ("Hanken Grotesk", "hanken-grotesk.woff2", "300 700", "normal"))
    out = []
    for family, name, weight, style in faces:
        data = base64.b64encode((ASSETS / "fonts" / name).read_bytes()).decode("ascii")
        out.append(f'@font-face {{ font-family: "{family}"; src: url(data:font/woff2;base64,{data}) format("woff2"); '
                   f"font-weight: {weight}; font-style: {style}; }}")
    return "\n".join(out)


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------

def build(ledger: Path, week_spec: str, tz_override=None, history_weeks: int = 4, draft: bool = False):
    """Return (html, meta, warnings) for one week's report."""
    cfg = wc.read_config(ledger)
    lang = lang_of(cfg.get("language", ""))
    s = STRINGS[lang]
    tzname = tz_override or cfg.get("timezone") or "UTC"
    try:
        tz = wc.ZoneInfo(tzname)
    except Exception:
        raise ReportError(f"unknown timezone {tzname!r}")
    start, end, label = wc.resolve_week(week_spec, tz)
    week_start, week_end = start.date(), end.date() - timedelta(days=1)

    report_path = ledger / "reports" / f"{label}.md"
    if not report_path.exists():
        raise ReportError(f"no report for {label}: write {report_path} first (see references/weekly-report-guide.md)")
    report = parse_report(report_path.read_text(encoding="utf-8"))
    status = (report["meta"].get("status") or "draft").strip().lower()
    if status == "draft" and not draft:
        raise ReportError(f"{label} is still a draft: the owner reviews it first (status: reviewed), "
                          "or pass --draft for a marked preview", code=3)

    checkins, _ = wc.parse_checkins(ledger)
    entries, _ = wc.parse_entries(ledger)
    week_entries = [e for e in entries if shareable(e) and start <= e["ts"] < end]
    entries_by_id = {e["id"]: e for e in entries}

    stamps = [c["ts"].astimezone(tz).date() for c in checkins]
    first = week_start - timedelta(days=7 * (max(history_weeks, 1) - 1))
    if stamps:
        first = max(first, min(min(stamps), week_start))
        first -= timedelta(days=first.weekday())
    series = daily_series(checkins, tz, first, week_end)
    week_days = [d for d in series if d["date"] >= week_start]
    prev_days = daily_series(checkins, tz, week_start - timedelta(days=7), week_start - timedelta(days=1))
    days_logged = [d for d in week_days if logged(d)]

    warnings = verbatim_warnings(report, entries_by_id, *ledger_corpus(ledger, entries))

    name = (cfg.get("name") or "").strip()
    therapist = (cfg.get("therapist_name") or "").strip()
    date_range = fmt_range(week_start, week_end, lang)

    parts = []
    conf = s["confidential"] + (" · " + s["for"].format(therapist=html.escape(therapist)) if therapist else "")
    parts.append(f'<header class="masthead"><div class="mark">{GLYPH}<span class="mark__word">sintr</span></div>'
                 f'<p class="masthead__conf">{conf}</p></header>')
    if status == "draft":
        parts.append(f'<p class="status"><span class="status__dot" aria-hidden="true"></span>{html.escape(s["draft"])}</p>')
    title_b = s["title_b"].format(name=html.escape(name)) if name else s["title_b_anon"]
    parts.append(f'<h1 class="title"><span class="title__a">{html.escape(date_range[:1].upper() + date_range[1:])}.</span> '
                 f'<span class="title__b">{title_b}</span></h1>')
    coverage = s["coverage"].format(n=len(days_logged))
    missing_days = [d["date"] for d in week_days if not logged(d)]
    if missing_days and days_logged:
        coverage += f'<span class="facts__sub">{s["coverage_missing"].format(days=fmt_weekdays(missing_days, lang))}</span>'
    facts = [(s["facts_week"], label), (s["facts_checkins"], coverage), (s["facts_moments"], str(len(week_entries)))]
    session = next_session(week_end, cfg, lang)
    if session:
        facts.append((s["facts_session"], html.escape(session)))
    parts.append('<dl class="facts">' + "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in facts) + "</dl>")

    def mood_block(lines):
        prose = [x for kind, x in blocks(lines) if kind == "p"]
        notes = [i for kind, x in blocks(lines) if kind == "ul" for i in x]
        out = [render_stats(week_days, prev_days, lang)] if days_logged else [f'<p class="quiet">{s["no_checkins"]}</p>']
        if prose:
            out.append('<div class="reading">' + "".join(f"<p>{inline(p)}</p>" for p in prose) + "</div>")
        if any(d[k] is not None for d in series for k in ("mood", "anxiety", "sleep_h")):
            chart_a, chart_b = sentiment_chart(series, week_start, lang)
            weeks = (len(series) + 6) // 7
            out.append(
                '<figure class="chart">'
                '<div class="chart__head">'
                f'<p class="chart__title">{s["chart_a"]}</p>'
                '<ul class="legend">'
                f'<li><svg viewBox="0 0 22 10" aria-hidden="true"><line x1="1" y1="5" x2="21" y2="5" stroke="{MOOD_COLOR}" stroke-width="2" stroke-linecap="round"/><circle cx="11" cy="5" r="3.4" fill="{MOOD_COLOR}"/></svg>{s["legend_mood"]}</li>'
                f'<li><svg viewBox="0 0 22 10" aria-hidden="true"><line x1="1" y1="5" x2="21" y2="5" stroke="{ANXIETY_COLOR}" stroke-width="2" stroke-linecap="round"/><circle cx="11" cy="5" r="3" fill="#fff" stroke="{ANXIETY_COLOR}" stroke-width="2"/></svg>{s["legend_anxiety"]}</li>'
                f'<li><svg viewBox="0 0 10 10" aria-hidden="true"><rect x="2" y="1" width="6" height="9" rx="1.5" fill="{SLEEP_COLOR}"/></svg>{s["legend_sleep"]}</li>'
                '</ul></div>'
                f"{chart_a}"
                f'<p class="chart__title chart__title--b">{s["chart_b"]}</p>'
                f"{chart_b}"
                f'<figcaption>{s["chart_note"].format(n=weeks)}</figcaption>'
                "</figure>")
        if days_logged:
            out.append(render_grid(week_days, week_entries, tz, lang))
        if notes:
            out.append(f'<div class="daynotes"><p class="daynotes__title">{s["day_notes"]}</p>{render_dated(notes, "obs obs--notes")}</div>')
        return "\n".join(out)

    sections = report["sections"]
    if days_logged and not any(sec["key"] == "mood" for sec in sections):
        at = next((i for i, sec in enumerate(sections) if sec["key"] not in COVER_KEYS), len(sections))
        sections = sections[:at] + [{"heading": s["sec_mood"], "key": "mood", "lines": []}] + sections[at:]
    cover, rest, suggested = parts, [], False
    for sec in sections:
        key, heading = sec["key"], inline(sec["heading"])
        lines = sec["lines"]
        if key not in COVER_KEYS:
            cover = rest
        if key == "week":
            body = render_blocks(lines, "lede")
        elif key == "session":
            body, suggested = render_topics(lines, lang)
        elif key == "mood":
            body = mood_block(lines)
        elif key == "moments":
            intro, moments = parse_moments(lines)
            body = render_blocks(intro, "intro") + "".join(
                render_moment(mo, entries_by_id.get(mo["entry_id"]), tz, lang) for mo in moments)
        elif key == "patterns":
            body = render_observations(lines)
        else:
            body = render_blocks(lines)
        cover.append(f'<section class="sec sec--{key or "other"}"><h2>{heading}</h2>{body}</section>')

    if (report["meta"].get("appendix") or "").strip().lower() in TRUE_WORDS and week_entries:
        cards = "".join(render_moment(entry_as_moment(e), e, tz, lang, compact=True) for e in week_entries)
        rest.append(f'<section class="sec sec--appendix"><h2>{s["appendix_title"]}</h2>'
                    f'<p class="intro">{s["appendix_intro"]}</p>{cards}</section>')

    # Page 1 is a letter: the title, how the week went, what to talk about,
    # and at its foot how the report was made and how to read it.
    if status == "draft":
        reviewed = ""
    else:
        reviewed = s["foot_reviewed"].format(name=html.escape(name)) if name else s["foot_reviewed_anon"]
    first_line = s["foot_prepared"].format(reviewed=reviewed) + " " + s["foot_observations"]
    if (cfg.get("report_disclaimer") or "true").strip().lower() != "false":
        first_line += " " + s["foot_clinical"]
    foot = [first_line, s["foot_quotes"]] + ([s["foot_suggested"]] if suggested else []) + [s["foot_realtime"]]
    parts.append('<footer class="foot">' + "".join(f"<p>{x}</p>" for x in foot) + "</footer>")
    parts = ['<div class="cover">' + "\n".join(parts) + "</div>"] + rest

    running = s["running"].format(name=name, week=label, conf=s["confidential"].lower()) if name \
        else f"sintr · {label} · {s['confidential'].lower()}"
    page_css = (f"@page {{ @bottom-left {{ content: {css_string(running)}; }} "
                '@bottom-right { content: counter(page) " / " counter(pages); } }')
    doc_title = f"{s['doc']} — {name} — {label}" if name else f"{s['doc']} — {label}"
    page = Template((ASSETS / "report.html").read_text(encoding="utf-8")).substitute(
        lang="pt-BR" if lang == "pt" else "en",
        title=html.escape(doc_title),
        fonts=font_faces(),
        css=(ASSETS / "report.css").read_text(encoding="utf-8"),
        page_css=page_css,
        light=LIGHT,
        body="\n".join(parts),
    )
    meta = {"week": label, "status": status, "lang": lang, "report": report_path,
            "sent_at": report["meta"].get("sent_at", "")}
    return page, meta, warnings


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def find_chrome():
    env = os.environ.get("SINTR_CHROME")
    if env:
        return env if Path(env).exists() or shutil.which(env) else None
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    cache = Path.home() / ".cache" / "ms-playwright"
    candidates += sorted((str(p) for p in cache.glob("chromium-*/chrome-*/chrome")), reverse=True)
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def render_playwright(html_path: Path, pdf_path: Path):
    """Playwright's own Chromium, else the installed Chrome or Edge through it.
    Returns a label for the browser used, or None."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    errors = []
    try:
        with sync_playwright() as p:
            for channel in (None, "chrome", "msedge"):
                try:
                    browser = p.chromium.launch(channel=channel) if channel else p.chromium.launch()
                except Exception as exc:  # browser not installed for this Playwright version
                    errors.append(f"{channel or 'chromium'}: {str(exc).splitlines()[0]}")
                    continue
                try:
                    page = browser.new_page()
                    page.goto(html_path.resolve().as_uri(), wait_until="load")
                    page.evaluate("document.fonts.ready")
                    page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
                finally:
                    browser.close()
                return f"playwright ({channel or 'chromium'} {browser.version})"
    except Exception as exc:
        errors.append(str(exc).splitlines()[0])
    print("sintr: playwright could not render: " + " | ".join(errors), file=sys.stderr)
    return None


def render_chrome(html_path: Path, pdf_path: Path, chrome: str) -> bool:
    with tempfile.TemporaryDirectory(prefix="sintr-chrome-") as profile:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
               "--disable-extensions", "--disable-background-networking", f"--user-data-dir={profile}",
               "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
               "--virtual-time-budget=10000", f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            cmd.insert(1, "--no-sandbox")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"sintr: {chrome} failed: {exc}", file=sys.stderr)
            return False
    if proc.returncode != 0 or not pdf_path.exists() or pdf_path.stat().st_size == 0:
        print(f"sintr: {chrome} exited {proc.returncode}: {proc.stderr.strip()[-400:]}", file=sys.stderr)
        return False
    return True


def render_pdf(html_path: Path, pdf_path: Path, renderer: str = "auto"):
    """Render with the first renderer that works. Returns its name or None."""
    if pdf_path.exists():
        pdf_path.unlink()
    if renderer in ("auto", "playwright"):
        used = render_playwright(html_path, pdf_path)
        if used:
            return used
    if renderer in ("auto", "chrome"):
        chrome = find_chrome()
        if chrome and render_chrome(html_path, pdf_path, chrome):
            return f"chrome ({chrome})"
    return None


def _private(path: Path):
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def main(argv=None):
    ap = argparse.ArgumentParser(description="sintr weekly report → PDF")
    ap.add_argument("--ledger", default="~/sintr", help="ledger path (default: ~/sintr)")
    ap.add_argument("--week", default="this", help="this | last | YYYY-Www (default: this)")
    ap.add_argument("--tz", default=None, help="IANA timezone (default: config.md timezone, else UTC)")
    ap.add_argument("--out", default=None, help="PDF path (default: <ledger>/reports/<week>.pdf)")
    ap.add_argument("--history-weeks", type=int, default=4, help="weeks shown in the sentiment chart (default: 4)")
    ap.add_argument("--draft", action="store_true", help="allow a draft report; the PDF is marked as a draft")
    ap.add_argument("--renderer", choices=("auto", "playwright", "chrome", "html"), default="auto",
                    help="auto tries Playwright, then a Chrome/Chromium binary; html writes only the HTML")
    ap.add_argument("--no-html", action="store_true", help="remove the HTML once the PDF is written")
    ap.add_argument("--strict", action="store_true", help="exit 5 if the verbatim check raises warnings")
    args = ap.parse_args(argv)

    ledger = Path(args.ledger).expanduser()
    if not ledger.is_dir():
        print(f"sintr: ledger not found: {ledger}", file=sys.stderr)
        return 2
    try:
        page, meta, warnings = build(ledger, args.week, args.tz, args.history_weeks, args.draft)
    except ReportError as exc:
        print(f"sintr: {exc}", file=sys.stderr)
        return exc.code

    suffix = ".draft" if meta["status"] == "draft" else ""
    pdf_path = Path(args.out).expanduser() if args.out else ledger / "reports" / f"{meta['week']}{suffix}.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = pdf_path.with_suffix(".html")
    html_path.write_text(page, encoding="utf-8")
    _private(html_path)

    for w in warnings:
        print(f"sintr: warning: {w}", file=sys.stderr)
    if meta["status"] == "sent":
        print(f"sintr: note: {meta['week']} was already sent ({meta['sent_at'] or 'time not recorded'}); "
              "this regenerates the file only", file=sys.stderr)

    if args.renderer == "html":
        print(f"sintr: wrote {html_path} (no PDF requested)")
        return 5 if args.strict and warnings else 0
    used = render_pdf(html_path, pdf_path, args.renderer)
    if not used:
        print(f"sintr: wrote {html_path}, but no PDF renderer was found.\n"
              "  Install Chrome/Chromium (or set SINTR_CHROME=/path/to/chrome), or `pip install playwright &&\n"
              "  playwright install chromium`; or open the HTML in a browser and print it to PDF\n"
              "  (A4, margins: default, background graphics: on).", file=sys.stderr)
        return 4
    _private(pdf_path)
    if args.no_html:
        html_path.unlink()
    print(f"sintr: wrote {pdf_path} via {used}" + ("" if args.no_html else f" (+ {html_path.name})"))
    if args.strict and warnings:
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
