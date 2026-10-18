.PHONY: test validate report-pdf example-pdf report-light install-hermes install-claude install-generic package site-deploy preview-site

LEDGER ?= $(HOME)/sintr
WEEK ?= this

test:
	python3 -m unittest discover -s scripts -p 'test_*.py' -v

validate: test
	@test -f skills/sintr/SKILL.md
	@test -f templates/sintr/README.md
	@test -f docs/INSTALL.md
	@test -f scripts/week_collect.py
	@test -f scripts/report_pdf.py
	@test -f scripts/report_assets/report.html
	@test -f scripts/report_assets/report.css
	@test -f scripts/report_assets/fonts/OFL.txt
	@test -f scripts/report_assets/light.jpg
	@test -f skills/sintr/references/report-framework.md
	@diff -r templates/sintr skills/sintr/templates/sintr
	@echo "repo checks: OK"

# The weekly report as a PDF, next to its Markdown: $(LEDGER)/reports/$(WEEK).pdf
#   make report-pdf WEEK=2026-W42 [LEDGER=~/sintr]
report-pdf:
	python3 scripts/report_pdf.py --ledger "$(LEDGER)" --week "$(WEEK)"

# Re-render the header light (report_assets/light-source.html -> light.jpg).
# Development only: needs uv and a Chromium for Playwright.
report-light:
	uv run --with playwright python scripts/render_light.py

# Rebuild the example PDF from the fictional fixture ledger.
example-pdf:
	python3 scripts/report_pdf.py --ledger scripts/fixtures/demo-ledger --week 2026-W42 --out docs/example-report.pdf --no-html

install-hermes:
	./installers/install.sh hermes "$${SINTR_LEDGER:-$$HOME/sintr}"

install-claude:
	./installers/install.sh claude-code "$${SINTR_LEDGER:-$$HOME/sintr}"

install-generic:
	./installers/install.sh generic "$${SINTR_LEDGER:-$$HOME/sintr}"

package:
	mkdir -p dist
	git archive --format=tar.gz --prefix=sintr/ -o dist/sintr-agent-pack.tar.gz HEAD

SITE_DEST ?= /home/hermes/artifacts/sintr
SITE_PORT ?= 8089

# Publish the static site. DESIGN-NOTES.md is repo documentation, not a page.
# The CDN caches CSS/JS for hours, so pages that link `styles.css?v=…` / `main.js?v=…`
# get the files' content hash stamped in: a changed file always gets a new URL.
site-deploy:
	mkdir -p $(SITE_DEST)
	rsync -a --exclude 'DESIGN-NOTES.md' site/ $(SITE_DEST)/
	@css=$$(sha1sum site/styles.css | cut -c1-10); js=$$(sha1sum site/main.js | cut -c1-10); \
	find $(SITE_DEST) -name '*.html' -exec sed -i \
	  -e "s/styles\.css?v=[A-Za-z0-9._-]*/styles.css?v=$$css/g" \
	  -e "s/main\.js?v=[A-Za-z0-9._-]*/main.js?v=$$js/g" {} + ; \
	echo "stamped styles.css?v=$$css main.js?v=$$js"

preview-site:
	python3 -m http.server $(SITE_PORT) --directory site
