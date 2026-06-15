"""
tests/test_challenge_2_bypass_html5.py
======================================
Тест-кейс для решения задачи Testing Challenge #2 - bypass html 5 validations
Стенд: http://testingchallenges.thetestingmap.org/challenge2.php
"""

import pytest
from playwright.sync_api import Page, expect

# ── Константы ─────────────────────────────────────────────────────────────────
CHALLENGE_2_URL = "http://testingchallenges.thetestingmap.org/challenge2.php"
INPUT_SELECTOR = 'input[name="valuesadded"]'
SUBMIT_SELECTOR = 'input[type="submit"]'


@pytest.mark.challenge2
@pytest.mark.dom_manipulation
def test_challenge2_bypass_html5_validation(page: Page) -> None:
    """
    Шаги:
      1. Открываем страницу Challenge #2.
      2. С помощью JS меняем тип инпута с "number" на "text",
         чтобы отключить встроенную HTML5-валидацию браузера на ввод только чисел.
      3. Вводим нечисловое значение (строку "bypassed").
      4. Отправляем форму.
      5. Проверяем, что отображается сообщение об успешном прохождении челенджа.
    """
    # 1. Открываем страницу
    page.goto(CHALLENGE_2_URL, wait_until="domcontentloaded")
    page.wait_for_selector(INPUT_SELECTOR)

    # 2. Меняем тип поля ввода на "text", чтобы обойти валидацию
    page.evaluate(f'document.querySelector(\'{INPUT_SELECTOR}\').setAttribute("type", "text")')

    # 3. Вводим нечисловое значение
    page.locator(INPUT_SELECTOR).fill("bypassed")

    # 4. Отправляем форму
    page.locator(SUBMIT_SELECTOR).click()

    # 5. Проверяем успешность прохождения
    expect(page.locator("body")).to_contain_text("YOU HAVE DONE IT")
