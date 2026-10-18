.PHONY: linting tests simulate all

# ── Linting ────────────────────────────────────────────────────────────────────
linting:
	uv run ruff format .
	uv run ruff check --fix --show-fixes --exit-non-zero-on-fix
	uv run mypy

# ── Tests ──────────────────────────────────────────────────────────────────────
tests:
	uv run pytest -m "not simulate and not simulation"

simulate:
	uv run pytest -m simulate

# ── Composite ──────────────────────────────────────────────────────────────────
all: linting tests
