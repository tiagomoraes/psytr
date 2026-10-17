.PHONY: test validate install-hermes install-claude install-generic package

test:
	python3 -m unittest discover -s scripts -p 'test_*.py' -v

validate: test
	@test -f skills/psytr/SKILL.md
	@test -f templates/psytr/README.md
	@test -f docs/INSTALL.md
	@test -f scripts/week_collect.py
	@echo "repo checks: OK"

install-hermes:
	./installers/install.sh hermes "$${PSYTR_LEDGER:-$$HOME/psytr}"

install-claude:
	./installers/install.sh claude-code "$${PSYTR_LEDGER:-$$HOME/psytr}"

install-generic:
	./installers/install.sh generic "$${PSYTR_LEDGER:-$$HOME/psytr}"

package:
	mkdir -p dist
	git archive --format=tar.gz --prefix=psytr/ -o dist/psytr-agent-pack.tar.gz HEAD
