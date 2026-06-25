PYTHON ?= python3

# Smart Money Tracker uses its own venv (uv-managed). The venv is the
# canonical interpreter for that skill. If SMT_VENV_PYTHON is not set,
# fall back to system python3 — which will work for `--help` only if
# the user has installed requests separately.
SMT_VENV_PYTHON ?= skills/smart-money-tracker/.venv/bin/python

# Daily Market Watch + Thematic Stock Picker are research/analysis-driven
# (no scripts; the SKILL.md is the contract). Their canonical outputs live
# in each skill's examples/ directory.

# Evals (cross-skill)
EVALS_DIR := evals
EVALS_RUNNER := run_evals.py
EVALS_ITERATION ?= iteration-1

.PHONY: help evals evals-smart-money evals-daily evals-thematic \
        smoke-smart-money clean verify lint

help:
	@echo "Targets:"
	@echo "  make evals                - run all 9 evals (3 per skill) and write benchmark"
	@echo "  make evals-smart-money    - run only the smart-money-tracker evals (3 prompts)"
	@echo "  make evals-daily          - run only the daily-market-watch evals (3 prompts)"
	@echo "  make evals-thematic       - run only the thematic-stock-picker evals (3 prompts)"
	@echo "  make smoke-smart-money    - smoke-test the scripts/ wrappers (--help)"
	@echo "  make verify               - smoke-smart-money + evals (full pre-PR gate)"
	@echo "  make clean                - remove __pycache__/, .pytest_cache/, *.pyc"
	@echo "  make lint                 - placeholder (no linter configured for these skills)"

# --- evals ---

evals:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION)

evals-smart-money:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION) --eval-set eval-0-smart-money

evals-daily:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION) --eval-set eval-1-daily

evals-thematic:
	cd $(EVALS_DIR) && $(PYTHON) $(EVALS_RUNNER) --iteration $(EVALS_ITERATION) --eval-set eval-2-thematic

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
