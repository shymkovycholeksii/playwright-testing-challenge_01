"""
conftest.py — global pytest-playwright configuration.

THROTTLING NOTE:
  The target server http://testingchallenges.thetestingmap.org/ blocks
  clients that exceed 30 requests/sec from a single IP.
  The delay is set via the --throttle-ms parameter (default: 200 ms)
  and is applied through slow_mo at the browser launch level.
"""

import pytest


# ── configuration ────────────────────────────────────────────────────────────


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "first_name: tests for the First Name field (TC01–TC15)")
    config.addinivalue_line(
        "markers",
        "dom_manipulation: tests with Cookie / JS / Page Source manipulation (TC16–TC18)",
    )
    config.addinivalue_line("markers", "challenge2: tests for Challenge #2 (Bypass HTML5 Validation)")
    config.addinivalue_line("markers", "challenge4: tests for Challenge #4 (Generate Testing Data)")
    config.addinivalue_line("markers", "challenge5: tests for Challenge #5 (Web Analytics Engine)")


def pytest_addoption(parser):
    """Add the --throttle-ms CLI option to control the slow_mo delay."""
    parser.addoption(
        "--throttle-ms",
        action="store",
        default="200",
        help="slow_mo delay between Playwright calls (ms). Default: 200.",
    )


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, pytestconfig):
    """
    Apply slow_mo at the browser launch level.

    slow_mo adds a delay (ms) after each Playwright call,
    ensuring the HTTP request rate to the server does not exceed
    1000 / slow_mo requests per second.
    """
    throttle = int(pytestconfig.getoption("--throttle-ms"))
    return {
        **browser_type_launch_args,
        "slow_mo": throttle,  # delay after each Playwright action
    }
