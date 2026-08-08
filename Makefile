PYTHON ?= python3

# Smart Money Tracker uses its own venv (uv-managed). The venv is the
# canonical interpreter for that skill. If SMT_VENV_PYTHON is not set,
# fall back to system python3 — which will work for `--help` only if
# the user has installed requests separately.
SMT_VENV_PYTHON ?= skills/smart-money-tracker/.venv/bin/python

# Daily Market Watch + Thematic Stock Picker + SG Financial Advisor are research/analysis-driven
# (no scripts; the SKILL.md is the contract). Their canonical outputs live
# in each skill's examples/ directory.

# Evals (cross-skill, research + weather-trading families)
EVALS_DIR := evals
EVALS_RUNNER := run_evals.py
EVALS_ITERATION ?= iteration-1

.PHONY: help evals evals-smart-money evals-daily evals-thematic evals-sg-fa \
        evals-news-rss \
        evals-weather evals-weather-wallet evals-weather-data-fetch \
        evals-weather-signal-gen evals-weather-risk-manage evals-weather-trade-execute \
        install-runtime smoke-smart-money test-news-rss clean verify lint

help:
	@echo "Targets:"
	@echo "  --- Research-skill evals (4 skills, 12 prompts, iteration-1) ---"
	@echo "  make evals                - run all 12 research + 15 weather evals (iteration-1 + iteration-2)"
	@echo "  make evals-smart-money    - run only the smart-money-tracker evals (3 prompts)"
	@echo "  make evals-daily          - run only the daily-market-watch evals (3 prompts)"
	@echo "  make evals-thematic       - run only the thematic-stock-picker evals (3 prompts)"
	@echo "  make evals-sg-fa          - run only the sg-financial-advisor evals (3 prompts)"
	@echo "  make evals-news-rss       - run only the news-rss-watch evals (3 prompts)"
	@echo "  --- Weather-trading skill evals (5 skills, 15 prompts, iteration-2) ---"
	@echo "  make evals-weather                  - run all 15 weather-trading evals"
	@echo "  make evals-weather-wallet           - run only polymarket-wallet-setup (3)"
	@echo "  make evals-weather-data-fetch       - run only weather-data-fetch (3)"
	@echo "  make evals-weather-signal-gen       - run only signal-gen (3)"
	@echo "  make evals-weather-risk-manage      - run only risk-manage (3)"
	@echo "  make evals-weather-trade-execute    - run only trade-execute (3)"
	@echo "  --- Weather-trading runtime (PRIVATE — separate repo) ---"
	@echo "  make install-runtime      - run scripts/install.sh to fetch + install the private runtime"
	@echo "  --- Housekeeping ---"
	@echo "  make test-news-rss      - run the 27 offline news-rss-watch unit tests"
	@echo "  make smoke-smart-money    - smoke-test the scripts/ wrappers (--help)"
	@echo "  make verify               - smoke-smart-money + evals (full pre-PR gate)"
	@echo "  make clean                - remove __pycache__/, .pytest_cache/, *.pyc"
	@echo "  make lint                 - placeholder (no linter configured for these skills)"

# --- evals (research family, iteration-1) ---

evals:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION)
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration iteration-2

evals-smart-money:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION) --eval-set eval-0-smart-money

evals-daily:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION) --eval-set eval-1-daily

evals-thematic:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION) --eval-set eval-2-thematic

# --- news-rss-watch unit tests (offline, stdlib unittest) ---

test-news-rss:
	$(PYTHON) -m unittest discover -s skills/news-rss-watch/tests

evals-sg-fa:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION) --eval-set eval-3-sgfa

evals-news-rss:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION) --eval-set eval-4-news-rss-watch

# --- weather-trading skill evals (iteration-2) ---

evals-weather:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration iteration-2

evals-weather-wallet:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration iteration-2 --eval-set eval-4-wallet

evals-weather-data-fetch:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration iteration-2 --eval-set eval-5-data-fetch

evals-weather-signal-gen:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration iteration-2 --eval-set eval-6-signal-gen

evals-weather-risk-manage:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration iteration-2 --eval-set eval-7-risk-manage

evals-weather-trade-execute:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration iteration-2 --eval-set eval-8-trade-execute

# --- weather-trading runtime install (downloads from a private location) ---

install-runtime:
	@command -v bash >/dev/null 2>&1 || { echo "ERROR: bash required."; exit 1; }
	./scripts/install.sh

# --- smoke test for the one script-driven skill ---

smoke-smart-money:
	@echo "--- skills/smart-money-tracker/scripts/smart_money.py --help ---"
	@if [ -x "$(SMT_VENV_PYTHON)" ]; then \
		$(SMT_VENV_PYTHON) skills/smart-money-tracker/scripts/smart_money.py --help 2>&1 | head -30; \
	else \
		echo "  (skills/smart-money-tracker/.venv/bin/python not found)"; \
		echo "  Run 'make install-smt' or 'cd skills/smart-money-tracker && uv sync' to create the venv."; \
	fi

# --- housekeeping ---

verify: smoke-smart-money evals

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	@echo "Cleaned __pycache__/, .pytest_cache/, *.pyc, *.pyo"

lint:
	@echo "No linter configured. Run your LSP for static analysis."
