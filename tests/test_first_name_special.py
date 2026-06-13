"""
tests/test_first_name_special.py
==================================
Тест-кейсы 16–18: Специфические проверки, требующие манипуляций
с DOM, Cookies и JavaScript на стенде:
http://testingchallenges.thetestingmap.org/index.php

THROTTLING NOTE (ВАЖНО):
    Целевой сервер блокирует IP при > 30 запросов в секунду.
    Между каждым навигационным вызовом page.goto() выставлена явная
    пауза INTER_TEST_DELAY_MS = 200 мс.  В сочетании со slow_mo = 200 мс
    (задаётся в conftest.py) суммарная задержка ≥ 400 мс между запросами,
    что соответствует ≈ 2.5 req/s — хорошо ниже лимита 30 req/s.
"""

import re

import pytest
from playwright.sync_api import BrowserContext, Page, expect

from tests.constants import (
    ADMIN_FIELD_SELECTOR,
    BASE_URL,
    FIRST_NAME_SELECTOR,
    INTER_TEST_DELAY_MS,
    SUBMIT_SELECTOR,
)


# ── Вспомогательные функции ───────────────────────────────────────────────────

def open_page(page: Page) -> None:
    """Открывает стенд с паузой-throttle перед запросом."""
    page.wait_for_timeout(INTER_TEST_DELAY_MS)
    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_selector(FIRST_NAME_SELECTOR)


def fill_and_submit(page: Page, value: str) -> None:
    """Вводит значение в First Name и отправляет форму."""
    page.locator(FIRST_NAME_SELECTOR).fill(value)
    page.locator(SUBMIT_SELECTOR).first.click()
    expect(page.locator("body")).to_contain_text("Checks found")


def page_text(page: Page) -> str:
    """Возвращает текстовое содержимое <body>."""
    return page.inner_text("body")


# ═══════════════════════════════════════════════════════════════════════════════
# TC16: You looked at the cookie
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.dom_manipulation
def test_tc16_you_looked_at_the_cookie(context: BrowserContext, page: Page) -> None:
    """
    TC16 — You looked at the cookie

    Шаги:
      1. Открыть страницу стенда.
      2. Прочитать все куки текущего домена через context.cookies().
      3. Найти куку, содержащую секретный токен (перебираем все куки;
         исключаем технические — session, PHPSESSID и т.п.).
      4. Извлечь значение (value) этой куки.
      5. Вставить значение в поле First Name и отправить форму.

    THROTTLING: пауза INTER_TEST_DELAY_MS мс перед page.goto() в open_page().
    """
    open_page(page)

    # ── 1. Читаем куки домена ─────────────────────────────────────────────────
    cookies = context.cookies(BASE_URL)
    assert cookies, "TC16: Куки не найдены. Возможно, страница не установила куки."

    # ── 2. Ищем токен-куку ────────────────────────────────────────────────────
    # Сайт обычно устанавливает куку с нестандартным именем (не PHPSESSID).
    # Алгоритм: берём первую куку, значение которой не пустое и
    # имя которой не является стандартным PHP-именем сессии.
    SKIP_NAMES = {"PHPSESSID", "session", "csrf_token", "__utma", "__ga"}

    token_value = None
    for cookie in cookies:
        if cookie["name"] not in SKIP_NAMES and cookie["value"].strip():
            raw_val = cookie["value"].strip()
            # Extract the actual token from the cookie value. 
            # Example cookie value: "You_have_checked_the_cookie_content._Add_oi32jnxd42390slk345_in_the_First_Name_field_to_mark_this_case."
            match = re.search(r"Add_([A-Za-z0-9]+)_in_the_First_Name", raw_val)
            if match:
                token_value = match.group(1)
                print(f"\n[TC16] Найдена кука: name={cookie['name']!r}, extracted token={token_value!r}")
                break
            else:
                # Fallback if the format is different
                token_value = raw_val
                print(f"\n[TC16] Найдена кука: name={cookie['name']!r}, raw value={token_value!r}")
                break

    # Если все куки «технические» — берём первую непустую (fallback)
    if token_value is None:
        for cookie in cookies:
            if cookie["value"].strip():
                token_value = cookie["value"].strip()
                print(f"\n[TC16] Fallback-кука: value={token_value!r}")
                break

    assert token_value is not None, (
        "TC16: Не удалось найти куку с токеном. "
        f"Все куки: {[c['name'] for c in cookies]}"
    )

    # ── 3. Вводим токен и сабмитим форму ─────────────────────────────────────
    fill_and_submit(page, token_value)

    # ── 4. Проверяем результат ────────────────────────────────────────────────
    body = page_text(page)
    check_name = "You looked at the cookie"
    assert check_name.lower() in body.lower(), (
        f"TC16: Чек '{check_name}' не засчитан.\n"
        f"Использованный токен: {token_value!r}\n"
        f"URL после сабмита: {page.url}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TC17: You looked at the page source
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.dom_manipulation
def test_tc17_you_looked_at_the_page_source(page: Page) -> None:
    """
    TC17 — You looked at the page source

    Шаги:
      1. Открыть страницу стенда.
      2. Получить HTML-исходник страницы через page.content().
      3. Regex-ом найти скрытый комментарий вида: <!-- secret_token -->.
         Паттерн ищет любой HTML-комментарий, не являющийся IE-conditional.
      4. Извлечь содержимое комментария (токен).
      5. Вставить токен в First Name и отправить форму.

    Из анализа страницы известно:
      <!-- if there is a missing resource add its name and extension to
           the FIRST NAME field in the page-->
    Этот комментарий является подсказкой для TC15 (Missing CSS).
    Сайт может содержать дополнительный скрытый комментарий — именно его
    мы ищем regex-паттерном.

    THROTTLING: пауза INTER_TEST_DELAY_MS мс перед page.goto() в open_page().
    """
    open_page(page)

    # ── 1. Получаем HTML-исходник ─────────────────────────────────────────────
    html_source = page.content()

    # ── 2. Ищем скрытый токен в комментарии ──────────────────────────────────
    # Ищем комментарий-подсказку про page source
    pattern = re.compile(r"validate that you have looked at the page source\s*:\s*([A-Za-z0-9]{15,})")
    
    token_value = None
    match = pattern.search(html_source)
    if match:
        token_value = match.group(1).strip()
        print(f"\n[TC17] Найден токен-комментарий: {token_value!r}")

    assert token_value is not None, (
        "TC17: Не удалось найти скрытый комментарий с токеном в HTML-исходнике.\n"
        "Проверьте исходник вручную: откройте страницу → View Source → ищите <!-- ... -->"
    )

    # ── 3. Вводим токен и сабмитим форму ─────────────────────────────────────
    fill_and_submit(page, token_value)

    # ── 4. Проверяем результат ────────────────────────────────────────────────
    body = page_text(page)
    check_name = "You looked at the page source"
    assert check_name.lower() in body.lower(), (
        f"TC17: Чек '{check_name}' не засчитан.\n"
        f"Использованный токен: {token_value!r}\n"
        f"URL после сабмита: {page.url}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TC18: You made the user admin
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.dom_manipulation
def test_tc18_you_made_the_user_admin(page: Page) -> None:
    """
    TC18 — You made the user admin

    Шаги:
      1. Открыть страницу стенда.
      2. С помощью page.evaluate() (выполнение JS в браузере) найти
         скрытый input[name="user_right_as_admin"] и изменить его value
         с '0' на '1'.
         Также снимаем атрибут 'hidden' на случай, если он есть.
      3. Заполнить First Name валидным значением.
      4. Отправить форму.

    THROTTLING: пауза INTER_TEST_DELAY_MS мс перед page.goto() в open_page().
    """
    open_page(page)

    # ── 1. Изменяем DOM через JavaScript ─────────────────────────────────────
    result = page.evaluate("""
        () => {
            // Ищем поле admin-права по атрибуту name
            const adminField = document.querySelector('input[name="user_right_as_admin"]');
            if (!adminField) {
                return { found: false, message: 'Элемент input[name="user_right_as_admin"] не найден' };
            }

            const oldValue = adminField.value;

            // Устанавливаем значение '1' (admin = true)
            adminField.value = '1';

            // Снимаем атрибуты hidden / disabled, если они есть
            adminField.removeAttribute('hidden');
            adminField.removeAttribute('disabled');
            adminField.type = 'text';   // делаем поле visible для Playwright

            return {
                found: true,
                oldValue: oldValue,
                newValue: adminField.value,
                message: 'OK'
            };
        }
    """)

    print(f"\n[TC18] Результат JS-манипуляции: {result}")

    assert result.get("found"), (
        "TC18: Поле input[name='user_right_as_admin'] не найдено на странице.\n"
        f"Сообщение: {result.get('message')}"
    )
    assert result.get("newValue") == "1", (
        f"TC18: Не удалось установить value='1'. Текущее value: {result.get('newValue')!r}"
    )

    # ── 2. Вводим имя и отправляем форму ─────────────────────────────────────
    fill_and_submit(page, "AdminTest")

    # ── 3. Проверяем результат ────────────────────────────────────────────────
    body = page_text(page)
    check_name = "You made the user admin"
    assert check_name.lower() in body.lower(), (
        f"TC18: Чек '{check_name}' не засчитан.\n"
        f"URL после сабмита: {page.url}\n"
        "Убедитесь, что поле user_right_as_admin существует на странице "
        "и форма отправляет его значение '1'."
    )
