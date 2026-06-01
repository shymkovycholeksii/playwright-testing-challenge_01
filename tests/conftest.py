"""
conftest.py — глобальная конфигурация pytest-playwright.

THROTTLING NOTE:
  Целевой сервер http://testingchallenges.thetestingmap.org/ блокирует
  клиентов при превышении 30 запросов/сек с одного IP.
  Задержка задаётся параметром --throttle-ms (по умолчанию 200 мс)
  и применяется через slow_mo на уровне запуска браузера.
"""

import pytest


# ── конфигурация ──────────────────────────────────────────────────────────────
# Задержка между запросами (мс).  ≥ 34 мс = < 30 req/s.
# Установлено 200 мс — безопасный запас с учётом RTT.
PAGE_DELAY_MS = 200


def pytest_configure(config):
    """Регистрируем кастомные маркеры."""
    config.addinivalue_line("markers", "first_name: тесты поля First Name (TC01–TC15)")
    config.addinivalue_line(
        "markers",
        "dom_manipulation: тесты с Cookie / JS / Page Source (TC16–TC18)",
    )


def pytest_addoption(parser):
    """Добавляем CLI-опцию --throttle-ms для управления паузой."""
    parser.addoption(
        "--throttle-ms",
        action="store",
        default=str(PAGE_DELAY_MS),
        help="Пауза slow_mo между Playwright-вызовами (мс). По умолчанию 200.",
    )


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, pytestconfig):
    """
    Устанавливаем slow_mo на уровне запуска браузера.

    slow_mo добавляет задержку (мс) после каждого Playwright-вызова —
    это гарантирует, что частота HTTP-запросов к серверу не превысит
    1000 / slow_mo запросов в секунду.
    """
    throttle = int(pytestconfig.getoption("--throttle-ms"))
    return {
        **browser_type_launch_args,
        "slow_mo": throttle,  # задержка после каждого Playwright-действия
    }
