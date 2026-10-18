#!/usr/bin/env python3
"""Tests for report_pdf.py — run with `python3 -m unittest discover -s scripts`.

The fixture ledger (scripts/fixtures/demo-ledger) is fictional and is also the
source of docs/example-report.pdf. Tests copy it to a temp dir before writing.
"""

import io
import os
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report_pdf as rp  # noqa: E402
import week_collect as wc  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "demo-ledger"
TZ = ZoneInfo("America/Sao_Paulo")


def copy_fixture(tmp: str) -> Path:
    dest = Path(tmp) / "ledger"
    shutil.copytree(FIXTURE, dest)
    return dest


def edit(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not in {path.name}"
    path.write_text(text.replace(old, new), encoding="utf-8")


class TestReportParsing(unittest.TestCase):
    def setUp(self):
        self.report = rp.parse_report((FIXTURE / "reports" / "2026-W42.md").read_text(encoding="utf-8"))

    def test_front_matter(self):
        meta = self.report["meta"]
        self.assertEqual(meta["week"], "2026-W42")
        self.assertEqual(meta["status"], "reviewed")
        self.assertEqual(meta["sent_to"], "")

    def test_sections_by_marker_in_order(self):
        keys = [s["key"] for s in self.report["sections"]]
        self.assertEqual(keys, list(rp.SECTION_KEYS))

    def test_sections_by_heading_without_marker(self):
        text = "## Resumo\nx\n\n## Para a sessão\n- z\n\n## Mood, energy & sleep\ny\n\n## Outra coisa\nw\n"
        keys = [s["key"] for s in rp.parse_report(text)["sections"]]
        self.assertEqual(keys, ["week", "session", "mood", None])

    def test_template_notes_dropped_markers_kept(self):
        text = ("## Como foi <!-- week -->\n<!--\nnote for the agent\nover lines\n-->\nA semana.\n\n"
                "## Momentos <!-- moments -->\n### Algo <!-- entry-2026-10-13-001 -->\n- did: x <!-- inline -->\n")
        report = rp.parse_report(text)
        self.assertEqual([s["key"] for s in report["sections"]], ["week", "moments"])
        self.assertNotIn("note for the agent", "\n".join(report["sections"][0]["lines"]))
        _, moments = rp.parse_moments(report["sections"][1]["lines"])
        self.assertEqual(moments[0]["entry_id"], "entry-2026-10-13-001")
        self.assertEqual(moments[0]["fields"]["did"], "x")

    def test_template_sections(self):
        template = FIXTURE.parents[2] / "templates" / "sintr" / "reports" / "YYYY-Www.md"
        report = rp.parse_report(template.read_text(encoding="utf-8"))
        self.assertEqual([s["key"] for s in report["sections"]], list(rp.SECTION_KEYS))
        _, moments = rp.parse_moments(next(s for s in report["sections"] if s["key"] == "moments")["lines"])
        self.assertEqual(moments[0]["entry_id"], "entry-YYYY-MM-DD-NNN")

    def test_docs_example_mirrors_fixture(self):
        docs = (FIXTURE.parents[2] / "docs" / "example-report.md").read_text(encoding="utf-8")
        self.assertIn((FIXTURE / "reports" / "2026-W42.md").read_text(encoding="utf-8"), docs)

    def test_disclaimer_dropped(self):
        last = "\n".join(self.report["sections"][-1]["lines"])
        self.assertNotIn("Não é avaliação clínica", last)

    def test_moments(self):
        sec = next(s for s in self.report["sections"] if s["key"] == "moments")
        intro, moments = rp.parse_moments(sec["lines"])
        self.assertEqual(len(moments), 4)
        first = moments[0]
        self.assertEqual(first["entry_id"], "entry-2026-10-13-001")
        self.assertEqual(first["fields"]["felt"], "ansiedade 85 ; frustração 60")
        self.assertIn("alternative", moments[1]["fields"])

    def test_field_continuation_lines(self):
        _, moments = rp.parse_moments(["### T", "- happened: first part", "  and the rest", "- did: x"])
        self.assertEqual(moments[0]["fields"]["happened"], "first part and the rest")

    def test_blocks(self):
        out = rp.blocks(["para one", "continues", "", "- a", "- b", "  more b", "", "tail"])
        self.assertEqual(out, [("p", "para one continues"), ("ul", ["a", "b more b"]), ("p", "tail")])


class TestInline(unittest.TestCase):
    def test_quotes_get_the_highlighter(self):
        self.assertEqual(rp.inline('disse "não vou dar conta" ontem'),
                         'disse <q class="said">não vou dar conta</q> ontem')
        self.assertIn('<q class="said">eu sempre decepciono</q>', rp.inline("“eu sempre decepciono”"))

    def test_escaping(self):
        out = rp.inline('<script>alert(1)</script> & "<b>"')
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)
        self.assertIn('<q class="said">&lt;b&gt;</q>', out)

    def test_emphasis(self):
        self.assertEqual(rp.inline("**forte** e *leve*"), "<strong>forte</strong> e <em>leve</em>")


class TestFormatting(unittest.TestCase):
    def test_numbers_follow_language(self):
        self.assertEqual(rp.fmt_num(2.833, "pt"), "2,8")
        self.assertEqual(rp.fmt_num(2.833, "en"), "2.8")
        self.assertEqual(rp.fmt_score(4.0, "pt"), "4")
        self.assertEqual(rp.fmt_score(3.5, "pt"), "3,5")

    def test_hours(self):
        self.assertEqual(rp.fmt_hours(6.8333), "6h50")
        self.assertEqual(rp.fmt_hours(8), "8h")
        self.assertEqual(rp.fmt_hours(5.5), "5h30")

    def test_ranges(self):
        self.assertEqual(rp.fmt_range(date(2026, 10, 12), date(2026, 10, 18), "pt"), "12 a 18 de outubro")
        self.assertEqual(rp.fmt_range(date(2026, 9, 28), date(2026, 10, 4), "pt"), "28 de setembro a 4 de outubro")
        self.assertEqual(rp.fmt_range(date(2026, 10, 12), date(2026, 10, 18), "en"), "October 12–18")

    def test_next_session(self):
        cfg = {"session_day": "Wednesday", "session_time": "18:00"}
        self.assertEqual(rp.next_session(date(2026, 10, 18), cfg, "pt"), "quarta, 21/10, 18h")
        self.assertEqual(rp.next_session(date(2026, 10, 18), {"session_day": "quarta"}, "en"), "Wednesday, 10/21")
        self.assertIsNone(rp.next_session(date(2026, 10, 18), {"session_day": ""}, "pt"))

    def test_language(self):
        self.assertEqual(rp.lang_of("pt-BR"), "pt")
        self.assertEqual(rp.lang_of("Português"), "pt")
        self.assertEqual(rp.lang_of("en"), "en")
        self.assertEqual(rp.lang_of(""), "en")


class TestChart(unittest.TestCase):
    def days(self):
        checkins, _ = wc.parse_checkins(FIXTURE)
        return rp.daily_series(checkins, TZ, date(2026, 9, 21), date(2026, 10, 18))

    def test_missing_days_stay_empty(self):
        by_day = {d["date"]: d for d in self.days()}
        self.assertIsNone(by_day[date(2026, 10, 14)]["mood"])  # no check-in on Wednesday
        self.assertEqual(by_day[date(2026, 10, 15)]["sleep_h"], 5.5)

    def test_deterministic(self):
        a1, b1 = rp.sentiment_chart(self.days(), date(2026, 10, 12), "pt")
        a2, b2 = rp.sentiment_chart(self.days(), date(2026, 10, 12), "pt")
        self.assertEqual((a1, b1), (a2, b2))

    def test_lines_break_at_gaps(self):
        days = [{"date": date(2026, 10, 12 + i), "mood": m, "energy": None, "anxiety": None, "sleep_h": None}
                for i, m in enumerate([3, 2, None, 2, 4, 4, 3])]
        svg, _ = rp.sentiment_chart(days, date(2026, 10, 12), "pt")
        mood_paths = re.findall(r'<path class="chart__line chart__line--mood" d="([^"]+)"', svg)
        self.assertEqual(len(mood_paths), 2)  # Mon–Tue, then Thu–Sun: nothing drawn across Wednesday
        self.assertEqual(mood_paths[0].count("L"), 1)
        self.assertEqual(mood_paths[1].count("L"), 3)

    def test_band_marks_the_week(self):
        svg, _ = rp.sentiment_chart(self.days(), date(2026, 10, 12), "pt")
        self.assertIn('class="chart__band"', svg)
        self.assertIn("esta semana", svg)


class TestVerbatim(unittest.TestCase):
    def test_fixture_is_clean(self):
        _, _, warnings = rp.build(FIXTURE, "2026-W42")
        self.assertEqual(warnings, [])

    def test_invented_quote_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "reports" / "2026-W42.md", '"ele acha que eu sou lento"', '"ele me odeia"')
            _, _, warnings = rp.build(ledger, "2026-W42")
            self.assertTrue(any("ele me odeia" in w and "not found" in w for w in warnings), warnings)

    def test_wrong_intensity_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "reports" / "2026-W42.md", "felt: ansiedade 85", "felt: ansiedade 95")
            _, _, warnings = rp.build(ledger, "2026-W42")
            self.assertTrue(any("ansiedade 95" in w and "85" in w for w in warnings), warnings)

    def test_unknown_entry_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "reports" / "2026-W42.md", "entry-2026-10-13-001", "entry-2026-10-13-009")
            _, _, warnings = rp.build(ledger, "2026-W42")
            self.assertTrue(any("entry-2026-10-13-009 not found" in w for w in warnings), warnings)

    def test_quote_from_private_entry_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "entries" / "2026-10.md", "- tags: família\n", "- tags: família\n- share: no\n")
            _, _, warnings = rp.build(ledger, "2026-W42")
            self.assertTrue(any("fazia tempo que eu não ria assim" in w and "share: no" in w for w in warnings), warnings)

    def test_strict_exit_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "reports" / "2026-W42.md", '"amanhã começa tudo de novo"', '"tudo de novo, de novo"')
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = rp.main(["--ledger", str(ledger), "--week", "2026-W42", "--renderer", "html", "--strict"])
            self.assertEqual(code, 5)


class TestBuild(unittest.TestCase):
    def test_document_content(self):
        page, meta, _ = rp.build(FIXTURE, "2026-W42")
        self.assertEqual(meta["week"], "2026-W42")
        self.assertIn('<html lang="pt-BR">', page)
        self.assertIn("12 a 18 de outubro.", page)
        self.assertIn("Confidencial · para Dra. Ana Exemplo", page)
        self.assertIn("quarta, 21/10, 18h", page)
        # coverage is honest: six of seven days, and which one is missing
        self.assertIn("6 de 7 dias", page)
        self.assertIn("sem check-in: qua", page)
        self.assertIn("<dt>Momentos registrados</dt><dd>5</dd>", page)
        for heading in ("Como foi a semana", "Humor, energia e sono", "Momentos que marcaram",
                        "O que se repetiu", "O que ajudou", "Para conversar na sessão"):
            self.assertIn(f"<h2>{heading}</h2>", page)
        # mood 3+2+2+4+4+3 over six check-ins, with its n and its extremes; Wednesday has none
        self.assertIn("3,0<span class=\"stat__unit\">de 5</span>", page)
        self.assertIn("média de 6 dias", page)
        self.assertIn("mín. 2 (ter, qui) · máx. 4 (sex, sáb)", page)
        self.assertIn('<td class="days__none">—</td>', page)
        self.assertIn("Nas palavras do dia", page)
        self.assertEqual(page.count('<article class="note">'), 4)

    def test_page_one_is_the_letter(self):
        page, _, _ = rp.build(FIXTURE, "2026-W42")
        cover = page.split('<div class="cover">', 1)[1].split('<section class="sec sec--mood">', 1)[0]
        self.assertIn("<h2>Como foi a semana</h2>", cover)
        self.assertIn("<h2>Para conversar na sessão</h2>", cover)
        self.assertIn('class="foot"', cover)
        self.assertLess(cover.index("Como foi a semana"), cover.index("Para conversar na sessão"))

    def test_moment_cards(self):
        page, _, _ = rp.build(FIXTURE, "2026-W42")
        self.assertIn('<span class="scale scale--tag">o mais forte</span>', page)  # the person's hot thought
        self.assertIn(f"70 {rp.ARROW} 45", page)  # re-rate after the alternative thought
        self.assertIn("acredita 55 de 100", page)
        self.assertIn("O que sustentava o pensamento", page)

    def test_suggestions_are_labeled(self):
        page, _, _ = rp.build(FIXTURE, "2026-W42")
        self.assertEqual(page.count('<span class="scale scale--tag">sugestão do sintr</span>'), 2)
        self.assertNotIn("(sugestão do sintr)", page)
        self.assertIn("Itens marcados como sugestão do sintr", page)

    def test_missing_core_field_reads_not_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "reports" / "2026-W42.md", "- did: Arrumou a mochila e viu um filme para desligar.\n", "")
            page, _, _ = rp.build(ledger, "2026-W42")
            self.assertEqual(page.count('<span class="none">não registrado</span>'), 1)

    def test_appendix_is_opt_in(self):
        page, _, _ = rp.build(FIXTURE, "2026-W42")
        self.assertNotIn("Todos os registros da semana", page)
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "reports" / "2026-W42.md", "status: reviewed", "status: reviewed\nappendix: true")
            page, _, warnings = rp.build(ledger, "2026-W42")
            self.assertIn("<h2>Todos os registros da semana</h2>", page)
            self.assertEqual(page.count('<article class="note note--compact">'), 5)
            self.assertIn("Jantar em família", page)  # not among the four moments, but an entry of the week
            self.assertNotIn("completed 2026-10-15", page)  # the agent's bookkeeping note stays in the ledger
            self.assertEqual(warnings, [])

    def test_self_contained(self):
        page, _, _ = rp.build(FIXTURE, "2026-W42")
        self.assertIsNone(re.search(r'(src|href)="https?:', page))
        self.assertIsNone(re.search(r"url\(['\"]?https?:", page))
        self.assertEqual(page.count("@font-face"), 3)

    def test_draft_is_refused_then_marked(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "reports" / "2026-W42.md", "status: reviewed", "status: draft")
            with self.assertRaises(rp.ReportError) as ctx:
                rp.build(ledger, "2026-W42")
            self.assertEqual(ctx.exception.code, 3)
            page, meta, _ = rp.build(ledger, "2026-W42", draft=True)
            self.assertEqual(meta["status"], "draft")
            self.assertIn('class="status"', page)
            self.assertIn("Não enviar", page)
            self.assertNotIn("revisado por Demo Person", page)

    def test_missing_report(self):
        with self.assertRaises(rp.ReportError) as ctx:
            rp.build(FIXTURE, "2026-W30")
        self.assertEqual(ctx.exception.code, 2)

    def test_not_shareable_entries_are_not_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "entries" / "2026-10.md", "- tags: família\n", "- tags: família\n- share: no\n")
            page, _, _ = rp.build(ledger, "2026-W42")
            self.assertIn("<dt>Momentos registrados</dt><dd>4</dd>", page)

    def test_english_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            edit(ledger / "config.md", "- language: pt-BR", "- language: en")
            page, _, _ = rp.build(ledger, "2026-W42")
            self.assertIn('<html lang="en">', page)
            self.assertIn("October 12–18.", page)
            self.assertIn("3.0<span class=\"stat__unit\">of 5</span>", page)
            self.assertIn("What went through their mind", page)

    def test_quiet_week_without_checkins(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            (ledger / "reports" / "2026-W30.md").write_text(
                "---\nweek: 2026-W30\nstatus: reviewed\n---\n\n## Como foi a semana <!-- week -->\n\nSemana quieta.\n",
                encoding="utf-8")
            page, _, warnings = rp.build(ledger, "2026-W30")
            self.assertIn("Semana quieta.", page)
            self.assertNotIn('class="chart"', page)
            self.assertNotIn('class="stats"', page)
            self.assertEqual(warnings, [])


class TestCli(unittest.TestCase):
    def test_html_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = rp.main(["--ledger", str(ledger), "--week", "2026-W42", "--renderer", "html"])
            self.assertEqual(code, 0)
            html_path = ledger / "reports" / "2026-W42.html"
            self.assertTrue(html_path.exists())
            self.assertEqual(html_path.stat().st_mode & 0o777, 0o600)
            self.assertFalse((ledger / "reports" / "2026-W42.pdf").exists())

    def test_missing_ledger(self):
        with redirect_stderr(io.StringIO()):
            self.assertEqual(rp.main(["--ledger", "/nonexistent/sintr", "--week", "2026-W42"]), 2)

    def test_render_pdf(self):
        if rp.find_chrome() is None:
            try:
                import playwright  # noqa: F401
            except ImportError:
                self.skipTest("no Chrome/Chromium or Playwright in this environment")
        with tempfile.TemporaryDirectory() as tmp:
            ledger = copy_fixture(tmp)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = rp.main(["--ledger", str(ledger), "--week", "2026-W42"])
            self.assertEqual(code, 0)
            pdf = ledger / "reports" / "2026-W42.pdf"
            data = pdf.read_bytes()
            self.assertTrue(data.startswith(b"%PDF-"))
            self.assertGreaterEqual(len(re.findall(rb"/Type\s*/Page[^s]", data)), 2)
            self.assertEqual(pdf.stat().st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
