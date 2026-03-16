# Phase 10 — Compliance & Reporting

This checklist confirms the build is exercised (not just audited) through tests and runtime wiring.

- Run full test suite: `python -m unittest discover -s tests`
- Ensure integration wiring passes: `tests/test_phase_integration.py`
- Confirm docs are up to date: `docs/PHASE_AUDIT.md` includes Phase 10
- Log outcomes in PR description or release notes when publishing
