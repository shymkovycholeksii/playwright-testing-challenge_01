"""
tests/test_challenge_2_bypass_html5.py
======================================
Test case for Testing Challenge #2 - Bypass HTML5 Validations
URL: http://testingchallenges.thetestingmap.org/challenge2.php
"""

import pytest
from playwright.sync_api import Page, expect

# ── Constants ────────────────────────────────────────────────────────────────
CHALLENGE_2_URL = "http://testingchallenges.thetestingmap.org/challenge2.php"
INPUT_SELECTOR = 'input[name="valuesadded"]'
SUBMIT_SELECTOR = 'input[type="submit"]'


@pytest.mark.challenge2
@pytest.mark.dom_manipulation
def test_challenge2_bypass_html5_validation(page: Page) -> None:
    """
    Steps:
      1. Navigate to the Challenge #2 page.
      2. Use JS to change the input type from "number" to "text",
         disabling the built-in HTML5 browser validation that restricts input to numbers only.
      3. Enter a non-numeric value (the string "bypassed").
      4. Submit the form.
      5. Verify that the challenge success message is displayed.
    """
    # 1. Navigate to the page
    page.goto(CHALLENGE_2_URL, wait_until="domcontentloaded")
    page.wait_for_selector(INPUT_SELECTOR)

    # 2. Change the input type to "text" to bypass validation
    page.evaluate(f'document.querySelector(\'{INPUT_SELECTOR}\').setAttribute("type", "text")')

    # 3. Enter a non-numeric value
    page.locator(INPUT_SELECTOR).fill("bypassed")

    # 4. Submit the form
    page.locator(SUBMIT_SELECTOR).click()

    # 5. Verify challenge completion
    expect(page.locator("body")).to_contain_text("YOU HAVE DONE IT")
