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
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
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
COVER_BUDGET_MM = 156  # what page 1 holds for them, in cover_mm() units
MOMENT_KEYS = ("when", "tags", "happened", "context", "thoughts", "felt", "body", "did",
               "evidence_for", "evidence_against", "alternative", "felt_after")

H2_RE = re.compile(r"^##\s+(.*?)\s*(?:<!--\s*([a-z_]+)\s*-->)?\s*$")
H1_RE = re.compile(r"^#\s+(.*?)\s*(?:<!--\s*([a-z_]+)\s*-->)?\s*$")
H3_RE = re.compile(r"^#{3,4}\s+(.*?)\s*(?:<!--\s*(entry-[\w-]+)\s*-->)?\s*$")
ANY_HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*$")
MOMENT_FIELD_RE = re.compile(r"^\s*[-*]\s*\**\s*([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ _-]{0,30}?)\s*\**\s*:\s*(.*)$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
TABLE_RE = re.compile(r"^\s*\|")
RULE_RE = re.compile(r"^\s*(\*\s*){3,}$|^\s*(_\s*){3,}$")
PLACEHOLDER_RE = re.compile(r"^\s*[-*]?\s*\{[^}]*\}\s*$")
QUOTE_PREFIX_RE = re.compile(r"^\s*>\s?")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍⭐⭕]")
LIST_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+(.*)$")
QUOTE_RE = re.compile(r"“([^”]+)”|\"([^\"]+)\"")
BELIEF_RE = re.compile(r"\((?:believability|acredito|credibilidade)\s*:?\s*(\d{1,3})\s*%?\)", re.I)
DATE_LEAD_RE = re.compile(r"^(.{1,40}?\d.{0,30}?)\s+[—–-]\s+(.+)$")
SUGGESTED_RE = re.compile(r"\s*\((?:sugest[aã]o do sintr|suggested by sintr)\)\s*\.?\s*$", re.I)
BOOKKEEPING_RE = re.compile(r"^(?:completed|corrected|correction|completad[oa]|corrigid[oa]|correção)\b", re.I)
TRUE_WORDS = ("true", "yes", "sim", "1")
STATUS_ALIASES = {"rascunho": "draft", "revisado": "reviewed", "revisada": "reviewed", "approved": "reviewed",
                  "aprovado": "reviewed", "aprovada": "reviewed", "enviado": "sent", "enviada": "sent"}
# Moment field names a model may use instead of the template's.
FIELD_ALIASES = {
    "situation": "happened", "what_happened": "happened", "event": "happened", "situacao": "happened",
    "o_que_aconteceu": "happened", "aconteceu": "happened",
    "thought": "thoughts", "automatic_thoughts": "thoughts", "pensamento": "thoughts", "pensamentos": "thoughts",
    "o_que_passou_pela_cabeca": "thoughts",
    "emotions": "felt", "emotion": "felt", "feelings": "felt", "feeling": "felt", "emocoes": "felt",
    "emocao": "felt", "sentiu": "felt", "o_que_sentiu": "felt", "sentimentos": "felt",
    "body_sensations": "body", "sensations": "body", "corpo": "body", "no_corpo": "body",
    "behavior": "did", "behaviour": "did", "action": "did", "response": "did", "fez": "did",
    "o_que_fez": "did", "comportamento": "did",
    "date": "when", "time": "when", "datetime": "when", "quando": "when", "data": "when",
    "tag": "tags", "area": "tags", "contexto": "context",
    "alternative_thought": "alternative", "balanced_thought": "alternative", "pensamento_alternativo": "alternative",
    "emotions_after": "felt_after", "rerate": "felt_after", "re_rate": "felt_after", "depois": "felt_after",
}

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
        "sec_week": "Como foi a semana",
        "sec_session": "Para conversar na sessão",
        "sec_mood": "Humor, energia e sono",
        "sec_moments": "Momentos que marcaram",
        "sec_patterns": "O que se repetiu",
        "sec_helped": "O que ajudou",
        "avg_mood": "Humor médio",
        "avg_energy": "Energia média",
        "avg_anxiety": "Ansiedade média",
        "avg_sleep": "Sono médio",
        "of5": "de 5",
        "per_night": "por noite",
        "n_days": "{n} dias",
        "n_day": "1 dia",
        "prev": "semana anterior: {v}",
        "prev_none": "sem semana anterior",
        "legend_mood": "Humor",
        "legend_anxiety": "Ansiedade",
        "this_week": "esta semana",
        "chart_a": "Humor e ansiedade, de 1 (baixo) a 5 (alto)",
        "chart_b": "Sono, em horas por noite",
        "chart_note": "Últimas {n} semanas, esta em destaque; os pontos são os check-ins desta semana. O trecho pontilhado atravessa dias sem check-in: nenhum valor é estimado.",
        "chart_alt": "Humor e ansiedade de {start} a {end}, de 1 a 5, e horas de sono por noite.",
        "grid_caption": "A semana dia a dia",
        "row_mood": "Humor",
        "row_energy": "Energia",
        "row_anxiety": "Ansiedade",
        "row_sleep": "Sono",
        "row_entries": "Momentos",
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
        "sec_week": "How the week went",
        "sec_session": "For the session",
        "sec_mood": "Mood, energy and sleep",
        "sec_moments": "Moments that stood out",
        "sec_patterns": "What repeated",
        "sec_helped": "What helped",
        "avg_mood": "Average mood",
        "avg_energy": "Average energy",
        "avg_anxiety": "Average anxiety",
        "avg_sleep": "Average sleep",
        "of5": "of 5",
        "per_night": "a night",
        "n_days": "{n} days",
        "n_day": "1 day",
        "prev": "week before: {v}",
        "prev_none": "no week before",
        "legend_mood": "Mood",
        "legend_anxiety": "Anxiety",
        "this_week": "this week",
        "chart_a": "Mood and anxiety, from 1 (low) to 5 (high)",
        "chart_b": "Sleep, in hours a night",
        "chart_note": "Last {n} weeks, this one highlighted; dots are this week's check-ins. A dotted stretch crosses days without a check-in: no value is estimated.",
        "chart_alt": "Mood and anxiety from {start} to {end}, 1 to 5, and hours of sleep per night.",
        "grid_caption": "The week day by day",
        "row_mood": "Mood",
        "row_energy": "Energy",
        "row_anxiety": "Anxiety",
        "row_sleep": "Sleep",
        "row_entries": "Moments",
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
SLEEP_COLOR = "#5c616b"       # graphite: sleep has its own panel and title, no categorical hue needed
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

def unwrap_fence(text: str) -> str:
    """A report pasted inside a ```markdown fence: drop the fence."""
    stripped = text.lstrip("﻿ \n")
    m = re.match(r"^(```|~~~)[\w-]*\n(.*?)(?:\n\1\s*)?$", stripped, flags=re.S)
    return m.group(2) if m else text


def parse_front_matter(text: str):
    meta, body = {}, text
    m = re.match(r"^﻿?\s*---\s*\n(.*?)\n---\s*\n?(.*)$", text, flags=re.S)
    if m:
        for line in m.group(1).splitlines():
            line = re.sub(r"\s+#.*$", "", line)
            km = re.match(r"^([A-Za-z_]+)\s*:\s*(.*)$", line.strip())
            if km:
                meta[km.group(1).lower()] = km.group(2).strip().strip("\"'")
        body = m.group(2)
    return meta, body


def report_status(meta: dict) -> str:
    raw = (meta.get("status") or "draft").strip().lower()
    return STATUS_ALIASES.get(raw, raw)


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


def clean_body(body: str, notes: list) -> str:
    """Bring a report written by any model back to the Markdown subset the
    PDF sets: tables, code fences, images, links, block quotes, inline code,
    emoji and template placeholders are taken out (and said so), never
    printed half-rendered."""
    out, seen = [], set()
    def note(kind, text):
        if kind not in seen:
            seen.add(kind)
            notes.append(text)
    for line in body.splitlines():
        if FENCE_RE.match(line):
            note("fence", "code fences were ignored")
            continue
        if TABLE_RE.match(line):
            note("table", "a table was left out: the PDF computes the check-in numbers and the grid itself")
            continue
        if PLACEHOLDER_RE.match(line):
            note("placeholder", "a template placeholder ({…}) was left out")
            continue
        if RULE_RE.match(line):
            continue
        line = QUOTE_PREFIX_RE.sub("", line)
        if IMAGE_RE.search(line):
            note("image", "images were left out")
            line = IMAGE_RE.sub("", line)
        line = LINK_RE.sub(r"\1", line)
        line = line.replace("`", "")
        if EMOJI_RE.search(line):
            note("emoji", "emoji were left out (the report's fonts have none)")
            line = EMOJI_RE.sub("", line).rstrip()
        out.append(line)
    return "\n".join(out)


def parse_report(text: str) -> dict:
    """Split a report into front matter, title and its sections, in the
    template's order. The disclaimer line under the last `---` is dropped:
    the PDF prints its own. `notes` lists what was normalized."""
    notes = []
    meta, body = parse_front_matter(unwrap_fence(text))
    body = clean_body(drop_comments(body), notes)
    lines = body.splitlines()
    # Sections are H2; an H1 after the title is read as a section too.
    title, sections, current, preamble = "", [], None, []
    for line in lines:
        m = H2_RE.match(line)
        if not m:
            h1 = H1_RE.match(line)
            if h1 and (title or section_key(h1.group(1), h1.group(2))):
                m = h1
            elif h1 and current is None:
                title = h1.group(1).strip()
                continue
        if m:
            current = {"heading": m.group(1).strip(), "key": section_key(m.group(1), m.group(2)), "lines": []}
            sections.append(current)
            continue
        (current["lines"] if current is not None else preamble).append(line)
    if any(l.strip() for l in preamble):
        # text before the first heading is never dropped: it opens the summary
        week = next((s for s in sections if s["key"] == "week"), None)
        if week is None:
            sections.insert(0, {"heading": "", "key": "week", "lines": preamble})
        else:
            week["lines"] = preamble + [""] + week["lines"]
        notes.append("text before the first section heading was kept as part of the summary")
    if sections:
        last = sections[-1]["lines"]
        for i, line in enumerate(last):
            if line.strip() == "---":
                del last[i:]
                break
    # One section per key, in the template's order; anything else after them.
    known, others, order = {}, [], [s["key"] for s in sections if s["key"]]
    for sec in sections:
        if sec["key"] in known:
            known[sec["key"]]["lines"] += [""] + sec["lines"]
            notes.append(f"two sections were read as {sec['key']!r} and merged")
        elif sec["key"]:
            known[sec["key"]] = sec
        else:
            others.append(sec)
    if order != sorted(order, key=SECTION_KEYS.index):
        notes.append("sections were put back in the template's order")
    sections = [known[k] for k in SECTION_KEYS if k in known] + others
    for sec in sections:
        if not sec["heading"] and sec["key"]:
            sec["heading"] = None  # filled with the default heading in the owner's language
    return {"meta": meta, "title": title, "sections": sections, "notes": notes}


def blocks(lines):
    """Group Markdown lines into ('p', text) and ('ul', [items]) blocks. A
    stray heading becomes a bold line."""
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
        hm = ANY_HEADING_RE.match(line)
        if hm:
            flush_para()
            items = None
            out.append(("p", f"**{hm.group(1).strip()}**"))
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


def field_key(raw: str) -> str:
    key = unicodedata.normalize("NFKD", raw.strip().lower())
    key = "".join(c for c in key if not unicodedata.combining(c))
    key = re.sub(r"[\s-]+", "_", key)
    return FIELD_ALIASES.get(key, key)


def parse_moments(lines):
    """`### Title <!-- entry-id -->` blocks with `- key: value` fields. Keys
    are read leniently (case, accents, bold, common synonyms)."""
    intro, moments, current = [], [], None
    for line in lines:
        m = H3_RE.match(line)
        if m:
            current = {"title": m.group(1).strip().strip("*"), "entry_id": m.group(2), "fields": {}, "rest": []}
            moments.append(current)
            continue
        if current is None:
            intro.append(line)
            continue
        fm = MOMENT_FIELD_RE.match(line)
        key = field_key(fm.group(1)) if fm else None
        if key in MOMENT_KEYS:
            current["fields"][key] = fm.group(2).strip().strip("*").strip()
            current["_last"] = key
        elif line.strip() and current.get("_last") and line.startswith((" ", "\t")):
            key = current["_last"]
            current["fields"][key] = current["fields"][key] + " " + line.strip()
        elif line.strip():
            current["rest"].append(line)
    for mo in moments:
        mo.pop("_last", None)
        mo["fields"] = {k: v for k, v in mo["fields"].items() if v}
    # a heading with nothing under it, or the template's own, is not a moment
    moments = [mo for mo in moments
               if (mo["fields"] or mo["rest"]) and "{" not in mo["title"] and "YYYY" not in (mo["entry_id"] or "")]
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
                    warnings.append(f"“{q}” ({sec['heading'] or sec['key']}): comes from an entry marked share: no — remove it")
                else:
                    warnings.append(f"“{q}” ({sec['heading'] or sec['key']}): not found in the ledger — quotes must be the person's exact words")
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
                said, _ = wc.parse_emotions(norm_emotions(mo["fields"].get(field, "")))
                recorded = {name.casefold(): value for name, value in source}
                for name, value in said:
                    if name.casefold() not in recorded:
                        warnings.append(f"moment {mo['title']!r}: emotion {name!r} is not in {eid}")
                    elif recorded[name.casefold()] != value:
                        warnings.append(f"moment {mo['title']!r}: {name} {value} but {eid} records {recorded[name.casefold()]}")
    return warnings


CAUSAL_RE = re.compile(r"\b(porque|por causa|causou|causad[oa]|devido a|levou a|fez com que|because|caused|due to|led to)\b", re.I)
LABEL_RE = re.compile(r"\b(catastrofiz\w*|ruminação|evitação|transtorno\w*|depressão|depressiv\w*|burnout|tdah|bipolar|"
                      r"borderline|trauma\w*|catastrophiz\w*|rumination|avoidance|disorder|depressive|adhd)\b", re.I)


def content_warnings(report: dict):
    """What a weaker model tends to get wrong and the verbatim check cannot
    see: length, unquoted thoughts, undated observations, causes, labels."""
    warnings = []
    for sec in report["sections"]:
        key, lines = sec["key"], sec["lines"]
        text = " ".join(l.strip() for l in lines)
        unquoted = QUOTE_RE.sub("", text)
        if key in ("week", "mood", "patterns", "helped", "session"):
            for m in sorted({m.group(0).lower() for m in CAUSAL_RE.finditer(unquoted)}):
                warnings.append(f"{sec['heading'] or sec['key']}: {m!r} states a cause — describe what happened together instead")
            for m in sorted({m.group(0).lower() for m in LABEL_RE.finditer(unquoted)}):
                warnings.append(f"{sec['heading'] or sec['key']}: {m!r} is a clinical label — use the person's words")
        if key == "week" and len(text.split()) > 140:
            warnings.append(f"{sec['heading'] or sec['key']}: {len(text.split())} words; the guide asks for 3–6 lines")
        items = [i for kind, v in blocks(lines) if kind == "ul" for i in v]
        if key == "session" and len(items) > 6:
            warnings.append(f"{sec['heading'] or sec['key']}: {len(items)} topics; keep 2–4")
        if key == "patterns":
            for item in items:
                if not re.search(r"\d", QUOTE_RE.sub("", item)):
                    warnings.append(f"{sec['heading'] or sec['key']}: observation without a date: {item[:60]!r}")
        if key == "moments":
            _, moments = parse_moments(lines)
            if len(moments) > 6:
                warnings.append(f"{sec['heading'] or sec['key']}: {len(moments)} moments; keep 3–5")
            for mo in moments:
                thoughts = mo["fields"].get("thoughts", "")
                if thoughts and not quotes_in(thoughts):
                    warnings.append(f"moment {mo['title']!r}: thoughts are not in quotes — copy them verbatim from the entry")
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
        days.append({"date": d, **{k: c.get(k) for k in ("mood", "energy", "anxiety", "sleep_h")}})
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


def _tangents(points):
    """Tangents for monotone cubic interpolation (Fritsch–Carlson, the same
    rule as d3's curveMonotoneX): the curve is smooth but never overshoots a
    recorded value, so it shows no peak or dip that is not in the data."""
    n = len(points)
    if n < 2:
        return [0.0] * n
    def sign(v):
        return (v > 0) - (v < 0)
    slopes = [(points[i + 1][1] - points[i][1]) / (points[i + 1][0] - points[i][0]) for i in range(n - 1)]
    t = [0.0] * n
    for i in range(1, n - 1):
        h0, h1 = points[i][0] - points[i - 1][0], points[i + 1][0] - points[i][0]
        s0, s1 = slopes[i - 1], slopes[i]
        p = (s0 * h1 + s1 * h0) / (h0 + h1)
        t[i] = (sign(s0) + sign(s1)) * min(abs(s0), abs(s1), 0.5 * abs(p))
    if n == 2:
        t[0] = t[1] = slopes[0]
    else:
        t[0] = (3 * slopes[0] - t[1]) / 2
        t[-1] = (3 * slopes[-1] - t[-2]) / 2
    return t


def _series(values, xs, y_of, in_week):
    """One continuous, smoothed series. Returns ({style: [path d]}, points)
    where style is past/now, plus `-gap` for a stretch that crosses days
    without a check-in (drawn dashed: the curve continues, the gap shows)."""
    pts = [(i, xs[i], y_of(v)) for i, v in enumerate(values) if v is not None]
    tangents = _tangents([(x, y) for _, x, y in pts])
    paths, style, d = {}, None, ""
    for k in range(len(pts) - 1):
        (i0, x0, y0), (i1, x1, y1) = pts[k], pts[k + 1]
        seg_style = ("now" if in_week[i0] else "past") + ("-gap" if i1 - i0 > 1 else "")
        dx = (x1 - x0) / 3
        curve = (f"C{_f(x0 + dx)} {_f(y0 + dx * tangents[k])} {_f(x1 - dx)} {_f(y1 - dx * tangents[k + 1])} "
                 f"{_f(x1)} {_f(y1)}")
        if seg_style != style:
            if d:
                paths.setdefault(style, []).append(d)
            style, d = seg_style, f"M{_f(x0)} {_f(y0)} "
        d += curve + " "
    if d:
        paths.setdefault(style, []).append(d.strip())
    return paths, pts


def _draw_series(out, values, xs, y_of, in_week, color):
    paths, pts = _series(values, xs, y_of, in_week)
    for style in ("past", "past-gap", "now-gap", "now"):
        for d in paths.get(style, []):
            cls = " ".join(["chart__line"] + [f"chart__line--{part}" for part in style.split("-")])
            out.append(f'<path class="{cls}" d="{d}" stroke="{color}"/>')
    if len(pts) == 1 and not in_week[pts[0][0]]:
        _, x, y = pts[0]
        out.append(f'<circle class="chart__dot chart__dot--past" cx="{_f(x)}" cy="{_f(y)}" r="2.4" fill="{color}"/>')
    return [(i, x, y) for i, x, y in pts if in_week[i]]


def sentiment_chart(days, week_start: date, lang: str):
    """Two small multiples on one day axis (never a dual axis): mood and
    anxiety on their shared 1–5 scale, then hours of sleep. Continuous
    smoothed lines; this week lit by the window light and dotted per day."""
    s = STRINGS[lang]
    n = len(days)
    W, left, right = 660.0, 30.0, 8.0
    slot = (W - left - right) / n
    xs = [left + slot * (i + 0.5) for i in range(n)]
    in_week = [d["date"] >= week_start for d in days]
    w0 = in_week.index(True) if True in in_week else n
    band_x, band_w = left + slot * w0, slot * (n - w0)

    # Panel A: mood and anxiety, 1-5 (0-5 if anyone recorded a 0).
    low = 0 if any((d[k] is not None and d[k] < 1) for d in days for k in ("mood", "anxiety")) else 1
    top, h = 22.0, 118.0
    def ya(v):
        return top + (5 - v) / (5 - low) * h
    alt = s["chart_alt"].format(start=fmt_day_month(days[0]["date"], lang), end=fmt_day_month(days[-1]["date"], lang))
    a = [f'<svg class="chart__svg" viewBox="0 0 {_f(W)} {_f(top + h + 12)}" role="img" aria-label="{html.escape(alt)}">']
    a.append('<defs><linearGradient id="wk-light" x1="0" y1="0" x2="1" y2="1">'
             f'<stop offset="0" stop-color="{LIGHT_STOPS[0]}"/><stop offset=".55" stop-color="{LIGHT_STOPS[1]}"/>'
             f'<stop offset="1" stop-color="{LIGHT_STOPS[2]}"/></linearGradient></defs>')
    if w0 < n:
        a.append(f'<rect class="chart__band" x="{_f(band_x)}" y="0" width="{_f(band_w)}" height="{_f(top + h + 12)}" rx="8" fill="url(#wk-light)"/>')
        a.append(f'<text class="chart__band-label" x="{_f(band_x + 8)}" y="13">{html.escape(s["this_week"])}</text>')
    for v in (low, 3, 5) if low == 0 else (1, 3, 5):
        y = ya(v)
        a.append(f'<line class="chart__grid" x1="{_f(left)}" x2="{_f(W - right)}" y1="{_f(y)}" y2="{_f(y)}"/>')
        a.append(f'<text class="chart__tick" x="{_f(left - 10)}" y="{_f(y + 3.5)}" text-anchor="end">{v}</text>')
    marks = {}
    for key, color in (("anxiety", ANXIETY_COLOR), ("mood", MOOD_COLOR)):
        marks[key] = _draw_series(a, [d[key] for d in days], xs, ya, in_week, color)
    # This week's days: anxiety as rings, mood as dots drawn on top, so a day
    # where both are equal reads as a dot inside a ring.
    for _, x, y in marks["anxiety"]:
        a.append(f'<circle class="chart__ring" cx="{_f(x)}" cy="{_f(y)}" r="4.4" stroke="{ANXIETY_COLOR}"/>')
    for _, x, y in marks["mood"]:
        a.append(f'<circle class="chart__dot" cx="{_f(x)}" cy="{_f(y)}" r="2.9" fill="{MOOD_COLOR}"/>')
    a.append("</svg>")

    # Panel B: hours of sleep, its own scale.
    sleep = [d["sleep_h"] for d in days]
    recorded = [v for v in sleep if v is not None]
    lo = min([4.0] + [float(int(v)) for v in recorded])
    hi = max([9.0] + [float(int(v) + (0 if float(v).is_integer() else 1)) for v in recorded])
    btop, bh, axis = 8.0, 50.0, 30.0
    base = btop + bh
    def yb(v):
        return base - (v - lo) / (hi - lo) * bh
    b = [f'<svg class="chart__svg" viewBox="0 0 {_f(W)} {_f(base + axis)}" aria-hidden="true">']
    if w0 < n:
        b.append(f'<rect class="chart__band" x="{_f(band_x)}" y="0" width="{_f(band_w)}" height="{_f(base + 4)}" rx="8" fill="url(#wk-light)"/>')
    for v in (4, 6, 8):
        if lo <= v <= hi:
            b.append(f'<line class="chart__grid" x1="{_f(left)}" x2="{_f(W - right)}" y1="{_f(yb(v))}" y2="{_f(yb(v))}"/>')
            b.append(f'<text class="chart__tick" x="{_f(left - 10)}" y="{_f(yb(v) + 3.5)}" text-anchor="end">{v}h</text>')
    for _, x, y in _draw_series(b, sleep, xs, yb, in_week, SLEEP_COLOR):
        b.append(f'<circle class="chart__dot" cx="{_f(x)}" cy="{_f(y)}" r="2.6" fill="{SLEEP_COLOR}"/>')
    # x axis: every day of the highlighted week, the first day of earlier weeks
    for i, d in enumerate(days):
        x = xs[i]
        if in_week[i]:
            b.append(f'<text class="chart__day" x="{_f(x)}" y="{_f(base + 15)}" text-anchor="middle">{html.escape(s["wd_short"][d["date"].weekday()])}</text>')
            b.append(f'<text class="chart__date" x="{_f(x)}" y="{_f(base + 26)}" text-anchor="middle">{d["date"].day}</text>')
        elif d["date"].weekday() == 0 or i == 0:
            b.append(f'<text class="chart__date" x="{_f(x)}" y="{_f(base + 15)}" text-anchor="middle">{fmt_day_month(d["date"], lang)}</text>')
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


def norm_emotions(raw: str) -> str:
    """`ansiedade 85, vergonha (55)` or `ansiedade 85/100 · vergonha 55%` ->
    `ansiedade 85 ; vergonha 55`, the ledger's form."""
    raw = re.sub(r"\s*/\s*100\b", "", raw or "").replace("%", "")
    raw = re.sub(r"\(\s*(\d{1,3})\s*\)", r"\1", raw)
    return re.sub(r"(\d)\s*[,·|]\s*", r"\1 ; ", raw)


def render_feelings(raw: str, lang: str, before=None) -> str:
    """Emotion chips with their 0–100 intensity; with `before`, a re-rate
    shows as `70 → 45`."""
    emotions, _ = wc.parse_emotions(norm_emotions(raw))
    if not emotions:
        return inline(raw)
    s, before = STRINGS[lang], {k.casefold(): v for k, v in (before or [])}
    chips = []
    for name, value in emotions:
        was = before.get(name.casefold())
        # the arrow is drawn: U+2192 is not in the embedded Latin subsets
        if was is not None:
            scale = f"{was} {ARROW} {value}"
        else:
            scale = f"{value} {s['of100']}" if value <= 100 else str(value)  # off the scale: shown as written
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
        row(s["m_felt_after"], render_feelings(f["felt_after"], lang, wc.parse_emotions(norm_emotions(f.get("felt", "")))[0]))
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
    """Four figures, each with the days it averages and the week before."""
    s = STRINGS[lang]
    cells = []
    for key, label in (("mood", "avg_mood"), ("energy", "avg_energy"), ("anxiety", "avg_anxiety"), ("sleep_h", "avg_sleep")):
        vals = [d[key] for d in week_days if d[key] is not None]
        if not vals:
            continue
        value, prev = sum(vals) / len(vals), avg([d[key] for d in prev_days])
        if key == "sleep_h":
            main = f'{fmt_hours(value)}<span class="stat__unit">{s["per_night"]}</span>'
            prev_txt = fmt_hours(prev) if prev is not None else None
        else:
            main = f'{fmt_num(value, lang)}<span class="stat__unit">{s["of5"]}</span>'
            prev_txt = fmt_num(prev, lang) if prev is not None else None
        sub = (s["n_days"].format(n=len(vals)) if len(vals) > 1 else s["n_day"]) + " · " + \
            (s["prev"].format(v=prev_txt) if prev_txt else s["prev_none"])
        cells.append(f'<div class="stat"><dt>{s[label]}</dt><dd class="stat__value">{main}</dd>'
                     f'<dd class="stat__sub">{sub}</dd></div>')
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
    marks = []
    for d in week_days:
        day_entries = per_day.get(d["date"], [])
        marks.append(f'<td class="days__marks">{"".join("<i></i>" for _ in day_entries)}</td>' if day_entries else none)
    rows.append(f'<tr><th scope="row">{s["row_entries"]}</th>{"".join(marks)}</tr>')
    return (f'<table class="days"><caption>{s["grid_caption"]}</caption><thead><tr><td></td>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def cover_mm(sections) -> float:
    """Rough height, in mm, of the page-1 sections as set by report.css (the
    summary in 12.5pt serif, the agenda in 11pt). Calibrated on the example."""
    mm = 0.0
    for sec in sections:
        mm += 21.0  # hairline, heading and their rests
        for kind, value in blocks(sec["lines"]):
            if kind == "p":
                per_line = 72 if sec["key"] == "week" else 92
                mm += 7.4 * math.ceil(len(value) / per_line) + 3.0
            else:
                mm += sum(6.3 * math.ceil(len(i) / 90) + 3.4 for i in value) + 3.0
    return mm


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
    status = report_status(report["meta"])
    if status not in ("draft", "reviewed", "sent"):
        report["notes"].append(f"status {status!r} is not draft/reviewed/sent: treated as a draft")
        status = "draft"
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

    warnings = ([f"normalized: {n}" for n in report["notes"]]
                + verbatim_warnings(report, entries_by_id, *ledger_corpus(ledger, entries))
                + content_warnings(report))

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
                f'<li><svg viewBox="0 0 22 10" aria-hidden="true"><line x1="1" y1="5" x2="21" y2="5" stroke="{MOOD_COLOR}" stroke-width="2" stroke-linecap="round"/><circle cx="11" cy="5" r="2.9" fill="{MOOD_COLOR}" stroke="#fff" stroke-width="1.5"/></svg>{s["legend_mood"]}</li>'
                f'<li><svg viewBox="0 0 22 10" aria-hidden="true"><line x1="1" y1="5" x2="21" y2="5" stroke="{ANXIETY_COLOR}" stroke-width="2" stroke-linecap="round"/><circle cx="11" cy="5" r="3.6" fill="#fff" stroke="{ANXIETY_COLOR}" stroke-width="1.8"/></svg>{s["legend_anxiety"]}</li>'
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
    cover, rest, suggested, cover_secs = parts, [], False, []
    for sec in sections:
        key, lines = sec["key"], sec["lines"]
        heading = inline(sec["heading"]) if sec["heading"] else s.get(f"sec_{key}", "")
        if key != "mood" and not any(l.strip() for l in lines):
            continue  # an empty heading (a leftover from the template) is not printed
        if key not in COVER_KEYS:
            cover = rest
        if cover is parts:
            cover_secs.append(sec)
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
    foot_html = '<footer class="foot">' + "".join(f"<p>{x}</p>" for x in foot) + "</footer>"
    # A letter too long for one page (a wordy summary, many topics) is not
    # squeezed: page 1 then flows like the rest, and the note closes the report.
    budget = COVER_BUDGET_MM - (10 if status == "draft" else 0) - (12 if len(name) > 28 else 0)
    if cover_mm(cover_secs) <= budget:
        parts = ['<div class="cover">' + "\n".join(parts + [foot_html]) + "</div>"] + rest
    else:
        warnings.append("page 1 is too long to fit (summary or topics); it flows onto page 2 — shorten them for the letter layout")
        parts = ['<div class="cover cover--flow">' + "\n".join(parts) + "</div>"] + rest + [foot_html]

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
