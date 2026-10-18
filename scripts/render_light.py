#!/usr/bin/env python3
"""Render report_assets/light-source.html to report_assets/light.jpg.

A development tool, run only when the light's design changes:
    make report-light        (uv run --with playwright python scripts/render_light.py)

The report embeds the resulting opaque JPEG instead of drawing the light in
the PDF, so every viewer shows the same thing (see light-source.html).
"""

import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "report_assets"
SCALE = 2.5  # 416 CSS px across 110mm: ~240 dpi, plenty for a blurred light


def main():
    from playwright.sync_api import sync_playwright

    out = ASSETS / "light.jpg"
    with sync_playwright() as p:
        for channel in (None, "chrome", "msedge"):
            try:
                browser = p.chromium.launch(channel=channel) if channel else p.chromium.launch()
                break
            except Exception:
                continue
        else:
            print("render_light: no Chromium for Playwright (playwright install chromium)", file=sys.stderr)
            return 1
        page = browser.new_page(device_scale_factor=SCALE, viewport={"width": 416, "height": 368})
        page.goto((ASSETS / "light-source.html").as_uri(), wait_until="load")
        page.locator(".box").screenshot(path=str(out), type="jpeg", quality=90)
        browser.close()
    print(f"render_light: wrote {out} ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
