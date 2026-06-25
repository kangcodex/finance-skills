# Smart Money Tracker — Test & Build Commands
# Usage: make <target>

.PHONY: help test test-unit test-integration test-e2e test-app test-skills \
        test-congress test-house-reps test-sec13f test-main test-compliance \
        test-source-audit test-no-network test-coverage build smoke clean

PYTHON := uv run python
PYTEST := uv run pytest

# ─── Quick Reference ──────────────────────────────────────────────────

help:
	@echo "Smart Money Tracker — Test Commands"
	@echo ""
	@echo "  make test              Run everything (unit + integration + app)"
	@echo "  make test-unit         Fast unit tests only"
	@echo "  make test-integration  Integration tests (no network)"
	@echo "  make test-e2e          E2E tests (requires Ollama running)"
	@echo "  make test-app          Application tests only (congress, 13f, main)"
	@echo "  make test-skills       Skill framework tests only"
	@echo "  make test-no-network   Exclude network-dependent tests"
	@echo "  make test-coverage     Run with coverage report"
	@echo "  make build             Build wheel"
	@echo "  make smoke             Smoke test all entrypoints"
	@echo "  make clean             Remove build artifacts"

# ─── Full Suite ───────────────────────────────────────────────────────

test:
	$(PYTEST) tests/ -v --tb=short

# ─── By Test Type ─────────────────────────────────────────────────────

test-unit:
	$(PYTEST) tests/skills/unit/ -v --tb=short

test-integration:
	$(PYTEST) tests/skills/integration/ -v --tb=short

test-e2e:
	OLLAMA_AVAILABLE=1 $(PYTEST) tests/skills/e2e/ -v --tb=short

# ─── By Application Module ────────────────────────────────────────────

test-app:
	$(PYTEST) tests/test_congress.py tests/test_house_reps.py \
	          tests/test_sec13f.py tests/test_main.py -v --tb=short

test-congress:
	$(PYTEST) tests/test_congress.py -v --tb=short

test-house-reps:
	$(PYTEST) tests/test_house_reps.py -v --tb=short

test-sec13f:
	$(PYTEST) tests/test_sec13f.py -v --tb=short -k "not Integration"

test-main:
	$(PYTEST) tests/test_main.py -v --tb=short

# ─── By Framework Area ────────────────────────────────────────────────

test-skills:
	$(PYTEST) tests/skills/ -v --tb=short

test-compliance:
	$(PYTEST) tests/test_skill_compliance.py -v --tb=short

test-source-audit:
	$(PYTEST) tests/test_source_audit.py -v --tb=short

# ─── Filtered / Specialized ───────────────────────────────────────────

test-no-network:
	$(PYTEST) tests/ -v --tb=short -k "not Integration and not E2E"

test-coverage:
	$(PYTEST) tests/ --cov=src --cov-report=term-missing --cov-report=html

# ─── Build & Verification ─────────────────────────────────────────────

build:
	$(PYTHON) -m build

smoke:
	@echo "--- main.py ---"
	$(PYTHON) src/smart_money_tracker/main.py --help
	@echo "--- congress.py ---"
	$(PYTHON) src/smart_money_tracker/congress.py --help 2>/dev/null || true
	@echo "--- sec13f.py ---"
	$(PYTHON) src/smart_money_tracker/sec13f.py --help 2>/dev/null || true
	@echo "--- house_reps.py ---"
	$(PYTHON) src/smart_money_tracker/house_reps.py --help 2>/dev/null || true

# ─── Cleanup ──────────────────────────────────────────────────────────

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/
	rm -rf tests/skills/reports/ tests/skills/baselines/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
