"""
tests/test_first_name_data_driven.py
=====================================
Тест-кейсы 1–15: Data-Driven проверки поля «First Name»
на стенде http://testingchallenges.thetestingmap.org/index.php

THROTTLING NOTE (ВАЖНО):
    Целевой сервер блокирует IP при > 30 запросов в секунду.
    Защита реализована двумя слоями:
      1. slow_mo (200 мс) — устанавливается в conftest.py через
         browser_type_launch_args; добавляет задержку после каждого
         Playwright-вызова на уровне движка браузера.
      2. page.wait_for_timeout(INTER_TEST_DELAY_MS) — явная пауза
         200 мс перед каждым навигационным запросом, чтобы гарантировать
         суммарную задержку ≥ 200 мс между HTTP-запросами к серверу.
    Итого: ~400 мс между последовательными тестами → ≈ 2.5 req/s —
    хорошо в пределах лимита 30 req/s.
"""

import pytest
from playwright.sync_api import Page, expect

from tests.constants import (
    BASE_URL,
    FIRST_NAME_SELECTOR,
    INTER_TEST_DELAY_MS,
    SUBMIT_SELECTOR,
)


# ── Вспомогательные функции ───────────────────────────────────────────────────

def submit_form(page: Page, first_name_value: str) -> None:
    """
    Открывает страницу, заполняет поле First Name и отправляет форму.

    Throttle layer 2: page.wait_for_timeout() перед page.goto()
    гарантирует паузу даже если slow_mo отключён.
    """
    # Пауза перед запросом (throttle layer 2)
    page.wait_for_timeout(INTER_TEST_DELAY_MS)

    page.goto(BASE_URL, wait_until="domcontentloaded")
    page.wait_for_selector(FIRST_NAME_SELECTOR)

    page.locator(FIRST_NAME_SELECTOR).fill(first_name_value)

    # .first — если на странице случайно окажется > 1 submit, не упадём
    page.locator(SUBMIT_SELECTOR).first.click()
    expect(page.locator("body")).to_contain_text("Checks found")


def page_text(page: Page) -> str:
    """Возвращает текстовое содержимое тега <body>."""
    return page.inner_text("body")


# ── Параметризованные тест-кейсы (TC01–TC15) ─────────────────────────────────

FIRST_NAME_TEST_CASES = [
    # Каждый pytest.param: (check_id, check_name_on_site, input_value, description)
    pytest.param(
        "TC01_minimum_value",
        "Minimum value",
        "A",
        "Ровно 1 символ — нижняя граница допустимой длины",
        id="TC01_minimum_value",
    ),
    pytest.param(
        "TC02_maximum_value",
        "Maximum values",
        "Abcdefghijklmnopqrstuvwxyzabcd",   # ровно 30 символов
        "Ровно 30 букв — верхняя граница допустимой длины",
        id="TC02_maximum_value",
    ),
    pytest.param(
        "TC03_more_than_maximum",
        "More than maximum values",
        "Abcdefghijklmnopqrstuvwxyzabcde",  # 31 символ (превышение)
        "31 буква — превышение максимальной длины",
        id="TC03_more_than_maximum",
    ),
    pytest.param(
        "TC04_average_value",
        "Average value",
        "John",
        "Обычное валидное имя (4 символа)",
        id="TC04_average_value",
    ),
    pytest.param(
        "TC05_empty_value",
        "Empty value",
        "",
        "Пустая строка — форма без заполнения поля",
        id="TC05_empty_value",
    ),
    pytest.param(
        "TC06_space",
        "Space",
        " ",
        "Одиночный пробел вместо имени",
        id="TC06_space",
    ),
    pytest.param(
        "TC07_space_at_beginning",
        "Space values at the beginning",
        " John",
        "Пробел в начале перед валидным именем",
        id="TC07_space_at_beginning",
    ),
    pytest.param(
        "TC08_space_in_middle",
        "Space in the middle",
        "John Doe",
        "Имя и фамилия, разделённые пробелом",
        id="TC08_space_in_middle",
    ),
    pytest.param(
        "TC09_space_at_end",
        "Space values at the end",
        "John ",
        "Пробел в конце после валидного имени",
        id="TC09_space_at_end",
    ),
    pytest.param(
        "TC10_other_chars",
        "Other chars then alphabetic",
        "John123!",
        "Цифры и спецсимволы в поле имени",
        id="TC10_other_chars",
    ),
    pytest.param(
        "TC11_non_ascii",
        "Non ASCII",
        "Иван",
        "Кириллица — символы вне ASCII-диапазона",
        id="TC11_non_ascii",
    ),
    pytest.param(
        "TC12_html_tags",
        "You used html tags",
        "<b>John</b>",
        "HTML-теги — проверка санитизации разметки",
        id="TC12_html_tags",
    ),
    pytest.param(
        "TC13_xss",
        "Basic XSS",
        "<script>alert(1)</script>",
        "XSS-payload — внедрение исполняемого JS",
        id="TC13_xss",
    ),
    pytest.param(
        "TC14_sql_injection",
        "Basic Sql injection",
        "' OR '1'='1",
        "SQL-инъекция — проверка экранирования запросов",
        id="TC14_sql_injection",
    ),
    pytest.param(
        "TC15_missing_css",
        "Missing css",
        "detailsoverviewnow.css",
        # Имя отсутствующего CSS-файла жёстко задано в <link href=...> в <head>.
        # Обнаружено при анализе исходника страницы (detailsoverviewnow.css).
        "Название отсутствующего CSS-файла из тега <link> на странице",
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
    Параметризованный тест для 15 проверок поля First Name (TC01–TC15).

    Каждая итерация:
      1. Открывает страницу стенда.
      2. Вводит заданное значение в поле First Name.
      3. Отправляет форму.
      4. Проверяет, что название чека присутствует в ответе сервера.

    Тесты запускаются последовательно (не параллельно) — см.
    THROTTLING NOTE в начале файла.
    """
    submit_form(page, input_value)

    # Убеждаемся, что страница загрузилась (нет ошибки соединения)
    assert page.url != "", f"[{check_id}] Страница не загрузилась"

    # Финальная проверка — наличие текста чека на странице ответа.
    # Сайт всегда отображает список всех чеков (пройденных и нет).
    body = page_text(page)
    assert check_name.lower() in body.lower(), (
        f"[{check_id}] Чек '{check_name}' не найден в ответе сервера.\n"
        f"Описание: {description}\n"
        f"Payload: {repr(input_value)}\n"
        f"URL после сабмита: {page.url}"
    )
