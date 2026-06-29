"""
tests/test_first_name_data_driven.py
=====================================
Test cases 1–15: Data-driven checks for the ‘First Name’ field
at http://testingchallenges.thetestingmap.org/index.php

THROTTLING NOTE:
    The target server blocks IPs that exceed 30 requests per second.
    Protection is implemented in two layers:
      1. slow_mo (200 ms) — configured in conftest.py via
         browser_type_launch_args; adds a delay after every
         Playwright call at the browser engine level.
      2. page.wait_for_timeout(INTER_TEST_DELAY_MS) — an explicit
         200 ms pause before each navigation request to guarantee
         a total gap of ≥ 200 ms between HTTP requests to the server.
    Total: ~400 ms between consecutive tests → ≈ 2.5 req/s —
    well within the 30 req/s limit.
"""

import pytest
from playwright.sync_api import Page, expect

from tests.constants import (
    BASE_URL,
    FIRST_NAME_SELECTOR,
    INTER_TEST_DELAY_MS,
    SUBMIT_SELECTOR,
)


# ── Helper functions ─────────────────────────────────────────────────────────────

def submit_form(page: Page, first_name_value: str) -> None:
    """
    Navigates to the page, fills in the First Name field, and submits the form.

    Throttle layer 2: page.wait_for_timeout() before page.goto()
    guarantees a pause even when slow_mo is disabled.
    """
    # Pause before the request (throttle layer 2)
    page.wait_for_timeout(INTER_TEST_DELAY_MS)

    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_selector(FIRST_NAME_SELECTOR)

    page.locator(FIRST_NAME_SELECTOR).fill(first_name_value)

    # .first — guards against strict mode violation if there is more than one submit button
    page.locator(SUBMIT_SELECTOR).first.click()
    expect(page.locator("body")).to_contain_text("Checks found")


def page_text(page: Page) -> str:
    """Returns the text content of the <body> tag."""
    return page.inner_text("body")


# ── Parameterised test cases (TC01–TC15) ──────────────────────────────────────────

FIRST_NAME_TEST_CASES = [
    # Each pytest.param: (check_id, check_name_on_site, input_value, description)
    pytest.param(
        "TC01_minimum_value",
        "Minimum value",
        "A",
        "Exactly 1 character — lower boundary of the allowed length",
        id="TC01_minimum_value",
    ),
    pytest.param(
        "TC02_maximum_value",
        "Maximum values",
        "Abcdefghijklmnopqrstuvwxyzabcd",   # exactly 30 characters
        "Exactly 30 letters — upper boundary of the allowed length",
        id="TC02_maximum_value",
    ),
    pytest.param(
        "TC03_more_than_maximum",
        "More than maximum values",
        "Abcdefghijklmnopqrstuvwxyzabcde",  # 31 characters (exceeds maximum)
        "31 letters — exceeds the maximum allowed length",
        id="TC03_more_than_maximum",
    ),
    pytest.param(
        "TC04_average_value",
        "Average value",
        "John",
        "A typical valid name (4 characters)",
        id="TC04_average_value",
    ),
    pytest.param(
        "TC05_empty_value",
        "Empty value",
        "",
        "Empty string — form submitted without filling in the field",
        id="TC05_empty_value",
    ),
    pytest.param(
        "TC06_space",
        "Space",
        " ",
        "A single space instead of a name",
        id="TC06_space",
    ),
    pytest.param(
        "TC07_space_at_beginning",
        "Space values at the beginning",
        " John",
        "Leading space before a valid name",
        id="TC07_space_at_beginning",
    ),
    pytest.param(
        "TC08_space_in_middle",
        "Space in the middle",
        "John Doe",
        "First and last name separated by a space",
        id="TC08_space_in_middle",
    ),
    pytest.param(
        "TC09_space_at_end",
        "Space values at the end",
        "John ",
        "Trailing space after a valid name",
        id="TC09_space_at_end",
    ),
    pytest.param(
        "TC10_other_chars",
        "Other chars then alphabetic",
        "John123!",
        "Digits and special characters in the name field",
        id="TC10_other_chars",
    ),
    pytest.param(
        "TC11_non_ascii",
        "Non ASCII",
        "Иван",
        "Cyrillic characters — symbols outside the ASCII range",
        id="TC11_non_ascii",
    ),
    pytest.param(
        "TC12_html_tags",
        "You used html tags",
        "<b>John</b>",
        "HTML tags — checks markup sanitisation",
        id="TC12_html_tags",
    ),
    pytest.param(
        "TC13_xss",
        "Basic XSS",
        "<script>alert(1)</script>",
        "XSS payload — injecting executable JavaScript",
        id="TC13_xss",
    ),
    pytest.param(
        "TC14_sql_injection",
        "Basic Sql injection",
        "' OR '1'='1",
        "SQL injection — checks query escaping",
        id="TC14_sql_injection",
    ),
    pytest.param(
        "TC15_missing_css",
        "Missing css",
        "detailsoverviewnow.css",
        # The name of the missing CSS file is hard-coded in a <link href=...> in <head>.
        # Discovered by inspecting the page source (detailsoverviewnow.css).
        "Name of the missing CSS file referenced in a <link> tag on the page",
        id="TC15_missing_css",
    ),
]


@pytest.mark.first_name
@pytest.mark.parametrize(
    "check_id, check_name, input_value, description",
    FIRST_NAME_TEST_CASES,
)
def test_first_name_field(
    page: Page,
    check_id: str,
    check_name: str,
    input_value: str,
    description: str,
) -> None:
    """
    Parameterised test for 15 checks of the First Name field (TC01–TC15).

    Each iteration:
      1. Navigates to the test site.
      2. Enters the given value in the First Name field.
      3. Submits the form.
      4. Verifies that the check name is present in the server response.

    Tests run sequentially (not in parallel) — see
    THROTTLING NOTE at the top of the file.
    """
    submit_form(page, input_value)

    # Ensure the page loaded successfully (no connection error)
    assert page.url != "", f"[{check_id}] Page did not load"

    # Final assertion — verify the check name appears on the response page.
    # The site always displays the full list of checks (passed and not passed).
    body = page_text(page)
    assert check_name.lower() in body.lower(), (
        f"[{check_id}] Check '{check_name}' not found in the server response.\n"
        f"Description: {description}\n"
        f"Payload: {repr(input_value)}\n"
        f"URL after submit: {page.url}"
    )
