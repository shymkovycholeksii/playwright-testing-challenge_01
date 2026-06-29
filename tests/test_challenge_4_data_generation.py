"""
tests/test_challenge_4_data_generation.py
=========================================
Test cases for Testing Challenge #4 - Generate Testing Data
URL: http://testingchallenges.thetestingmap.org/challenge4.php
"""

import pytest
from playwright.sync_api import Page, expect

# ── Constants ────────────────────────────────────────────────────────────────
CHALLENGE_4_URL = "http://testingchallenges.thetestingmap.org/challenge4.php"
INPUT_SELECTOR = 'input[name="CNP"]'
SUBMIT_SELECTOR = 'input[type="submit"]'
INTER_TEST_DELAY_MS = 200


@pytest.fixture(scope="module")
def shared_page(browser):
    """
    Shared browser context and page fixture scoped to the module.
    This is required because the site tracks the number of successfully submitted CNPs
    within a single session (via cookies).
    """
    context = browser.new_context()
    page = context.new_page()
    page.wait_for_timeout(INTER_TEST_DELAY_MS)
    page.goto(CHALLENGE_4_URL, wait_until="domcontentloaded")
    yield page
    context.close()


@pytest.mark.challenge4
@pytest.mark.dom_manipulation
class TestChallenge4:
    """
    Romanian CNP specification (13 digits):
    - Digit 1: Gender and birth century (1,2 - 1900-1999; 3,4 - 1800-1899; 5,6 - 2000-2099; 7,8 - foreign residents; 9 - non-residents)
    - Digits 2-3: Last two digits of birth year
    - Digits 4-5: Birth month (01-12)
    - Digits 6-7: Birth day (01-31)
    - Digits 8-9: Region code (01-52)
    - Digits 10-12: Sequential number (000-999)
    - Digit 13: Check digit (sum of first 12 digits multiplied by weights '279146358279' modulo 11; if remainder is 10, check digit is 1)
    """

    def test_tc1_male_born_2000s(self, shared_page):
        """TC1: Male, born on 20 May 2016 (first digit: 5)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("5160520011230")
        page.locator(SUBMIT_SELECTOR).click()
        expect(page.locator("span.values-tested")).to_have_text("1")

    def test_tc2_female_born_2000s(self, shared_page):
        """TC2: Female, born on 30 November 2018 (first digit: 6)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("6181130424565")
        page.locator(SUBMIT_SELECTOR).click()
        expect(page.locator("span.values-tested")).to_have_text("2")

    def test_tc3_male_born_1900s(self, shared_page):
        """TC3: Male, born on 1 January 1999 (first digit: 1)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("1990101157898")
        page.locator(SUBMIT_SELECTOR).click()
        expect(page.locator("span.values-tested")).to_have_text("3")

    def test_tc4_female_born_1900s(self, shared_page):
        """TC4: Female, born on 25 December 1980 (first digit: 2)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("2801225529992")
        page.locator(SUBMIT_SELECTOR).click()
        expect(page.locator("span.values-tested")).to_have_text("4")

    def test_tc5_foreign_resident(self, shared_page):
        """TC5: Foreign citizen, resident in Romania (first digit: 7)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("7220714331116")
        page.locator(SUBMIT_SELECTOR).click()
        # The last step should complete the challenge
        expect(page.locator("body")).to_contain_text("YOU HAVE DONE IT")
