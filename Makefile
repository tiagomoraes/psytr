.PHONY: test validate install-hermes install-claude install-generic package

test:
	python3 -m unittest discover -s scripts -p 'test_*.py' -v

validate: test
	@test -f skills/sintr/SKILL.md
	@test -f templates/sintr/README.md
	@test -f docs/INSTALL.md
	@test -f scripts/week_collect.py
	@echo "repo checks: OK"

install-hermes:
	./installers/install.sh hermes "$${SINTR_LEDGER:-$$HOME/sintr}"

install-claude:
	./installers/install.sh claude-code "$${SINTR_LEDGER:-$$HOME/sintr}"

install-generic:
	./installers/install.sh generic "$${SINTR_LEDGER:-$$HOME/sintr}"

package:
	mkdir -p dist
	git archive --format=tar.gz --prefix=sintr/ -o dist/sintr-agent-pack.tar.gz HEAD
