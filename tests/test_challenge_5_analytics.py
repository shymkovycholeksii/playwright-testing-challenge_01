"""
tests/test_challenge_5_analytics.py
===================================
Test case for Testing Challenge #5 - Using a Web Analytics Engine
URL: http://testingchallenges.thetestingmap.org/challenge5.php
"""

import pytest
from playwright.sync_api import Page, expect

# ── Constants ────────────────────────────────────────────────────────────────
CHALLENGE_5_URL = "http://testingchallenges.thetestingmap.org/challenge5.php"
ANALYTICS_URL_PATTERN = "http://webanalyticsengine.thetestingmap.org/web_analytics_engine.php"
SUBMIT_SELECTOR = 'input[type="submit"]'
INTER_TEST_DELAY_MS = 200


@pytest.mark.challenge5
@pytest.mark.dom_manipulation
def test_challenge5_analytics_engine_down(page: Page) -> None:
    """
    Steps:
      1. Set up Playwright network request interception to block
         requests to the external analytics engine (simulating it being down / unreachable).
      2. Navigate to the Challenge #5 page.
      3. Click the "Submit" button on the registration form.
      4. Because the analytics request is blocked, it will fail with an error.
         The client-side timer in challenge.js will abort the request after 10 seconds,
         report the failure to the local server, and reload the page.
      5. Wait for the timeout and page reload to complete, then verify
         that the challenge success message is present.
    """
    # 1. Block requests to the analytics engine
    page.route(ANALYTICS_URL_PATTERN, lambda route: route.abort("failed"))

    # 2. Navigate to the page
    page.wait_for_timeout(INTER_TEST_DELAY_MS)
    page.goto(CHALLENGE_5_URL, wait_until="domcontentloaded")

    # 3. Click the form submit button
    page.locator(SUBMIT_SELECTOR).click()

    # 4. Wait 10.5 seconds for the client-side setTimeout (10000ms) in challenge.js
    # to fire and trigger the page reload
    page.wait_for_timeout(10500)

    # 5. Verify challenge completion
    expect(page.locator("body")).to_contain_text("YOU HAVE DONE IT")
