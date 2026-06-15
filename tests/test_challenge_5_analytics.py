"""
tests/test_challenge_5_analytics.py
===================================
Тест-кейс для решения задачи Testing Challenge #5 - using a web analytics engine
Стенд: http://testingchallenges.thetestingmap.org/challenge5.php
"""

import pytest
from playwright.sync_api import Page, expect

# ── Константы ─────────────────────────────────────────────────────────────────
CHALLENGE_5_URL = "http://testingchallenges.thetestingmap.org/challenge5.php"
ANALYTICS_URL_PATTERN = "http://webanalyticsengine.thetestingmap.org/web_analytics_engine.php"
SUBMIT_SELECTOR = 'input[type="submit"]'
INTER_TEST_DELAY_MS = 200


@pytest.mark.challenge5
@pytest.mark.dom_manipulation
def test_challenge5_analytics_engine_down(page: Page) -> None:
    """
    Шаги:
      1. Настраиваем перехват сетевых запросов в Playwright для блокировки
         запросов к внешнему аналитическому движку (имитация его падения/недоступности).
      2. Открываем страницу Challenge #5.
      3. Нажимаем кнопку "Submit" на форме регистрации.
      4. Из-за блокировки аналитики, запрос к ней завершится ошибкой.
         Встроенный на странице таймер (challenge.js) через 10 секунд прервет запрос (abort),
         отправит отчет о падении на локальный сервер и перезагрузит страницу.
      5. Ожидаем завершения таймаута и перезагрузки, после чего проверяем
         наличие сообщения об успешном прохождении челенджа.
    """
    # 1. Блокируем запросы к аналитическому движку
    page.route(ANALYTICS_URL_PATTERN, lambda route: route.abort("failed"))

    # 2. Открываем страницу
    page.wait_for_timeout(INTER_TEST_DELAY_MS)
    page.goto(CHALLENGE_5_URL, wait_until="domcontentloaded")

    # 3. Нажимаем кнопку сабмита формы
    page.locator(SUBMIT_SELECTOR).click()

    # 4. Ждем 10.5 секунд, чтобы сработал клиентский setTimeout (10000ms) в challenge.js
    # и выполнилась перезагрузка страницы
    page.wait_for_timeout(10500)

    # 5. Проверяем успешность прохождения челенджа
    expect(page.locator("body")).to_contain_text("YOU HAVE DONE IT")
