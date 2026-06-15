"""
tests/test_challenge_4_data_generation.py
=========================================
Тест-кейсы для решения задачи Testing Challenge #4 - generate testing data
Стенд: http://testingchallenges.thetestingmap.org/challenge4.php
"""

import pytest
from playwright.sync_api import Page, expect

# ── Константы ─────────────────────────────────────────────────────────────────
CHALLENGE_4_URL = "http://testingchallenges.thetestingmap.org/challenge4.php"
INPUT_SELECTOR = 'input[name="CNP"]'
SUBMIT_SELECTOR = 'input[type="submit"]'
INTER_TEST_DELAY_MS = 200


@pytest.fixture(scope="module")
def shared_page(browser):
    """
    Фикстура общего браузерного контекста и страницы на уровне модуля.
    Это необходимо, так как сайт отслеживает количество успешно введенных CNP
    в рамках одной сессии (через cookies).
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
    Спецификация румынского CNP (13 цифр):
    - 1-я цифра: Пол и век рождения (1,2 - 1900-1999; 3,4 - 1800-1899; 5,6 - 2000-2099; 7,8 - резиденты-иностранцы; 9 - нерезиденты)
    - 2-3 цифры: Последние две цифры года рождения
    - 4-5 цифры: Месяц рождения (01-12)
    - 6-7 цифры: День рождения (01-31)
    - 8-9 цифры: Код региона (01-52)
    - 10-12 цифры: Порядковый номер (000-999)
    - 13-я цифра: Контрольное число (сумма первых 12 цифр, умноженных на веса '279146358279' по модулю 11; если остаток 10, то контрольная цифра 1)
    """

    def test_tc1_male_born_2000s(self, shared_page):
        """TC1: Мужчина, родился 20 мая 2016 года (первая цифра 5)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("5160520011230")
        page.locator(SUBMIT_SELECTOR).click()
        expect(page.locator("span.values-tested")).to_have_text("1")

    def test_tc2_female_born_2000s(self, shared_page):
        """TC2: Женщина, родилась 30 ноября 2018 года (первая цифра 6)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("6181130424565")
        page.locator(SUBMIT_SELECTOR).click()
        expect(page.locator("span.values-tested")).to_have_text("2")

    def test_tc3_male_born_1900s(self, shared_page):
        """TC3: Мужчина, родился 1 января 1999 года (первая цифра 1)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("1990101157898")
        page.locator(SUBMIT_SELECTOR).click()
        expect(page.locator("span.values-tested")).to_have_text("3")

    def test_tc4_female_born_1900s(self, shared_page):
        """TC4: Женщина, родилась 25 декабря 1980 года (первая цифра 2)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("2801225529992")
        page.locator(SUBMIT_SELECTOR).click()
        expect(page.locator("span.values-tested")).to_have_text("4")

    def test_tc5_foreign_resident(self, shared_page):
        """TC5: Иностранный гражданин, резидент в Румынии (первая цифра 7)"""
        page = shared_page
        page.wait_for_timeout(INTER_TEST_DELAY_MS)
        page.locator(INPUT_SELECTOR).fill("7220714331116")
        page.locator(SUBMIT_SELECTOR).click()
        # Последний шаг должен завершить челендж
        expect(page.locator("body")).to_contain_text("YOU HAVE DONE IT")
