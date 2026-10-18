#!/usr/bin/env python3
"""sintr website: build the translated home pages.

The English home (site/index.html) is the source. Elements carrying
data-i18n="key" have their inner HTML translated; data-i18n-attr="attr:key;..."
translates attribute values. Each locale lives in i18n/<code>.json:

    {"locale": "pt-BR", "strings": {key: html}, "source": {key: english html}}

"source" records the English text each string was translated from, so a later
change to the English copy shows up as stale instead of silently drifting.

Usage:
    python3 i18n/build.py              extract en.json, validate, build all pages
    python3 i18n/build.py --check CODE  validate one locale file (no writes)
    python3 i18n/build.py --stamp CODE  record the current English as "source"

Stdlib only. Exit 1 on errors (missing keys, broken markup, lost tokens).
"""

from __future__ import annotations

import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
I18N = ROOT / "i18n"
CONFIG = json.loads((I18N / "locales.json").read_text(encoding="utf-8"))
SOURCE = ROOT / CONFIG["source"]
BASE_URL = CONFIG["base_url"]
LOCALES = CONFIG["locales"]
KEEP = CONFIG.get("keep_tokens", {})
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

# Strings the build itself renders (language menu, footer list).
EXTRA_EN = {
    "ui.language": "Language",
    "ui.this_page_in": "This page in",
}


# ───────────────────────── parsing ─────────────────────────

class Spans(HTMLParser):
    """Collect the source spans of translatable inner HTML and attribute values."""

    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.line_starts = [0]
        for m in re.finditer("\n", text):
            self.line_starts.append(m.end())
        self.stack = []      # (tag, key or None, inner_start)
        self.inner = []      # (key, start, end)
        self.attrs = []      # (key, start, end)
        self.local_name = [] # (start, end): inner HTML that becomes the locale's own name
        self.local_lang = [] # (start, end): a lang="" value that becomes the locale's code
        self.feed(text)
        self.close()

    def _abs(self) -> int:
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs, selfclosing=False):
        start = self._abs()
        raw = self.get_starttag_text()
        end = start + len(raw)
        amap = dict(attrs)
        for pair in filter(None, (amap.get("data-i18n-attr") or "").split(";")):
            name, key = pair.split(":", 1)
            m = re.search(r'\s' + re.escape(name) + r'="([^"]*)"', raw)
            if not m:
                raise SystemExit(f"attribute {name!r} not found on <{tag}> for key {key}")
            self.attrs.append((key, start + m.start(1), start + m.end(1)))
        if amap.get("data-i18n-local") == "lang":
            m = re.search(r'\slang="([^"]*)"', raw)
            self.local_lang.append((start + m.start(1), start + m.end(1)))
        if tag in VOID or selfclosing:
            return
        self.stack.append((tag, amap.get("data-i18n"), end, amap.get("data-i18n-local")))

    def handle_startendtag(self, tag, attrs):
        # <path/>, <rect/>…: attributes only, nothing to close
        self.handle_starttag(tag, attrs, selfclosing=True)

    def handle_endtag(self, tag):
        pos = self._abs()
        while self.stack:
            t, key, inner_start, local = self.stack.pop()
            if key:
                self.inner.append((key, inner_start, pos))
            if local == "name":
                self.local_name.append((inner_start, pos))
            if t == tag:
                break


def extract(text: str) -> dict:
    sp = Spans(text)
    found = [(s, k, text[s:e]) for k, s, e in sp.inner] + [(s, k, text[s:e]) for k, s, e in sp.attrs]
    found.sort()
    out = {}
    for _, key, value in found:
        if key in out and out[key] != value:
            raise SystemExit(f"key {key} used twice with different text")
        out[key] = value
    out.update(EXTRA_EN)
    return out


# ───────────────────────── validation ─────────────────────────

TAG = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>")


def tag_shape(s: str):
    return [(c, n.lower(), re.sub(r"\s+", " ", a.strip())) for c, n, a in TAG.findall(s)]


def validate(code: str, data: dict, en: dict) -> tuple[list, list]:
    errors, warnings = [], []
    strings = data.get("strings", {})
    source = data.get("source", {})
    for key, en_val in en.items():
        if key not in strings:
            errors.append(f"{code}: missing key {key}")
            continue
        val = strings[key]
        if not isinstance(val, str) or not val.strip():
            errors.append(f"{code}: empty value for {key}")
            continue
        if tag_shape(val) != tag_shape(en_val):
            errors.append(f"{code}: markup differs in {key}\n    en: {tag_shape(en_val)}\n    {code}: {tag_shape(val)}")
        for tok in KEEP.get(key, []):
            if tok not in val:
                errors.append(f"{code}: {key} must keep {tok!r} exactly")
        if en_val.count("sintr") != val.count("sintr"):
            warnings.append(f"{code}: {key} mentions 'sintr' {val.count('sintr')}x (English: {en_val.count('sintr')}x)")
        if source and key in source and source[key] != en_val:
            warnings.append(f"{code}: {key} is stale (the English changed since it was translated)")
    for key in strings:
        if key not in en:
            warnings.append(f"{code}: unused key {key}")
    return errors, warnings


# ───────────────────────── rendering ─────────────────────────

def rel_prefix(loc) -> str:
    return "../" if loc["path"] else ""


def page_url(loc) -> str:
    return BASE_URL + (loc["path"] + "/" if loc["path"] else "")


def link_to(target, here) -> str:
    """Relative link from page `here` to the home of `target`."""
    if not here["path"]:
        return (target["path"] + "/") if target["path"] else "./"
    return "../" + (target["path"] + "/" if target["path"] else "?lang=en")


def head_region(loc, t) -> str:
    lines = []
    if not loc["path"]:
        paths = {l["detect"]: l["path"] + "/" for l in LOCALES if l["path"]}
        lines += [
            "  <script>",
            "    /* First visit: follow the browser's language list (the same list it sends as",
            "       Accept-Language). A language picked in the menu always wins. */",
            "    (function () {",
            "      var paths = " + json.dumps(paths, ensure_ascii=False, separators=(",", ":")) + ";",
            "      try {",
            "        if (/[?&]lang=en\\b/.test(location.search)) { localStorage.setItem('sintr-lang', 'en'); return; }",
            "        var saved = localStorage.getItem('sintr-lang');",
            "        if (saved) { if (paths[saved]) location.replace(paths[saved] + location.hash); return; }",
            "        var prefs = navigator.languages || [navigator.language || ''];",
            "        for (var i = 0; i < prefs.length; i++) {",
            "          var tag = String(prefs[i]).toLowerCase(), base = tag.split('-')[0];",
            "          if (base === 'en') return;",
            "          if (base === 'zh' && /-(tw|hk|mo|hant)\\b/.test(tag)) continue;",
            "          if (paths[base]) { location.replace(paths[base] + location.hash); return; }",
            "        }",
            "      } catch (e) {}",
            "    })();",
            "  </script>",
        ]
    for l in LOCALES:
        lines.append(f'  <link rel="alternate" hreflang="{l["lang"]}" href="{page_url(l)}">')
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{BASE_URL}">')
    lines.append(f'  <meta property="og:locale" content="{loc["og"]}">')
    for l in LOCALES:
        if l is not loc:
            lines.append(f'  <meta property="og:locale:alternate" content="{l["og"]}">')
    return "\n".join(lines) + "\n"


GLOBE = ('<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
         '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.3 2.3 3.5 5.2 3.5 8.5s-1.2 6.2-3.5 8.5'
         'M12 3.5C9.7 5.8 8.5 8.7 8.5 12s1.2 6.2 3.5 8.5"/></svg>')


def switcher_region(loc, t) -> str:
    label = html.escape(t["ui.language"], quote=True)
    items = []
    for l in LOCALES:
        cur = ' aria-current="true"' if l is loc else ""
        items.append(f'            <li><a href="{link_to(l, loc)}" hreflang="{l["lang"]}" lang="{l["lang"]}" '
                     f'data-lang="{l["detect"]}"{cur}>{l["name"]}</a></li>')
    return ("        <details class=\"langs\">\n"
            f"          <summary class=\"langs__toggle\" aria-label=\"{label}: {html.escape(loc['name'], quote=True)}\">"
            f"{GLOBE}<span>{loc['short']}</span></summary>\n"
            f"          <ul class=\"langs__menu\" aria-label=\"{label}\">\n" + "\n".join(items) + "\n"
            "          </ul>\n"
            "        </details>\n")


def footer_region(loc, t) -> str:
    links = []
    for l in LOCALES:
        cur = ' aria-current="true"' if l is loc else ""
        links.append(f'<a href="{link_to(l, loc)}" hreflang="{l["lang"]}" lang="{l["lang"]}" data-lang="{l["detect"]}"{cur}>{l["name"]}</a>')
    return (f'      <nav class="foot__langs" aria-label="{html.escape(t["ui.language"], quote=True)}">'
            f'<span>{t["ui.this_page_in"]}</span> ' + " ".join(links) + "</nav>\n")


def replace_region(text: str, name: str, body: str) -> str:
    pat = re.compile(r"(<!-- i18n:" + re.escape(name) + r" -->\n)(.*?)([ \t]*<!-- /i18n:" + re.escape(name) + r" -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"region {name} missing in source")
    return pat.sub(lambda m: m.group(1) + body + m.group(3), text, count=1)


def drop_region(text: str, name: str) -> str:
    pat = re.compile(r"[ \t]*<!-- i18n:" + re.escape(name) + r" -->.*?<!-- /i18n:" + re.escape(name) + r" -->\n?", re.S)
    return pat.sub("", text, count=1)


def render(loc, strings: dict, source_text: str) -> str:
    text = source_text
    if loc["path"]:
        sp = Spans(text)
        edits = []
        for key, s, e in sp.inner:
            edits.append((s, e, strings[key]))
        for key, s, e in sp.attrs:
            edits.append((s, e, strings[key].replace('"', "&quot;")))
        for s, e in sp.local_name:
            edits.append((s, e, loc["name"]))
        for s, e in sp.local_lang:
            edits.append((s, e, loc["lang"]))
        for s, e, new in sorted(edits, key=lambda x: x[0], reverse=True):
            text = text[:s] + new + text[e:]
        text = re.sub(r'<html lang="[^"]*"', f'<html lang="{loc["lang"]}"', text, count=1)
        text = text.replace(f'<link rel="canonical" href="{BASE_URL}">', f'<link rel="canonical" href="{page_url(loc)}">')
        text = text.replace(f'<meta property="og:url" content="{BASE_URL}">', f'<meta property="og:url" content="{page_url(loc)}">')
        # pages one level down reach shared files with ../
        text = re.sub(r'\b(href|src)="(?!https?:|#|/|tel:|mailto:|data:|\.\./|\?)([^"]*)"',
                      lambda m: f'{m.group(1)}="../{m.group(2)}"', text)
        if loc.get("report") == "original-only":
            text = drop_region(text, "report-toggle")
            text = drop_region(text, "report-local")
    text = replace_region(text, "head", head_region(loc, strings))
    text = replace_region(text, "switcher", switcher_region(loc, strings))
    text = replace_region(text, "footer-langs", footer_region(loc, strings))
    return text


# ───────────────────────── commands ─────────────────────────

def load_locale(code: str) -> dict:
    p = I18N / f"{code}.json"
    if not p.exists():
        raise SystemExit(f"missing {p.relative_to(ROOT)}")
    return json.loads(p.read_text(encoding="utf-8"))


def main(argv):
    source_text = SOURCE.read_text(encoding="utf-8")
    en = extract(source_text)

    if len(argv) == 2 and argv[0] in ("--check", "--stamp"):
        code = argv[1]
        data = load_locale(code)
        errors, warnings = validate(code, data, en)
        for w in warnings:
            print("warning:", w)
        for e in errors:
            print("error:", e)
        if errors:
            return 1
        if argv[0] == "--stamp":
            data["source"] = {k: en[k] for k in en if k in data["strings"]}
            (I18N / f"{code}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"stamped {code}")
        else:
            print(f"{code}: ok ({len(en)} keys)")
        return 0
    if argv:
        print(__doc__)
        return 2

    (I18N / "en.json").write_text(json.dumps({"locale": "en", "strings": en}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    failed = False
    for loc in LOCALES:
        if not loc["path"]:
            strings = en
        else:
            if not (I18N / f"{loc['code']}.json").exists():
                print(f"warning: {loc['code']} not translated yet, page skipped")
                continue
            data = load_locale(loc["code"])
            errors, warnings = validate(loc["code"], data, en)
            for w in warnings:
                print("warning:", w)
            for e in errors:
                print("error:", e)
            if errors:
                failed = True
                continue
            strings = data["strings"]
        out = render(loc, strings, source_text)
        target = SOURCE if not loc["path"] else SOURCE.parent / loc["path"] / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out, encoding="utf-8")
        print(f"built {target.relative_to(ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
