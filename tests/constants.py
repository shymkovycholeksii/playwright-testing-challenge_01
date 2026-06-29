"""
tests/constants.py
==================
Centralized constants for the entire test suite.

All values used in more than one file are defined here.
When the environment changes (base URL, timeouts), only this
file needs to be updated — all test files will pick up the changes automatically.
"""

# ── Base URL ──────────────────────────────────────────────────────────────────
BASE_URL = "http://testingchallenges.thetestingmap.org/index.php"

# ── Throttling ────────────────────────────────────────────────────────────────
# The server blocks clients exceeding > 30 req/s from a single IP.
# ≥ 34 ms = < 30 req/s; 200 ms is a safe margin accounting for RTT.
INTER_TEST_DELAY_MS = 200

# ── Form locators ─────────────────────────────────────────────────────────────
# Use the name/type attribute — resilient to markup changes.
FIRST_NAME_SELECTOR  = 'input[name="firstname"]'
# .first — guards against strict mode violation if there is more than one submit button
SUBMIT_SELECTOR      = 'input[type="submit"], button[type="submit"]'
ADMIN_FIELD_SELECTOR = 'input[name="user_right_as_admin"]'
