# Testing Challenges — Playwright UI Test Suite

Набор автоматизированных UI-тестов на **Python + Playwright** для покрытия
18 проверок поля «First Name» на стенде
[testingchallenges.thetestingmap.org](http://testingchallenges.thetestingmap.org/index.php).

---

## Структура проекта

```
Project_Test_Playwright/
├── conftest.py                          # Глобальная конфигурация pytest-playwright
├── pytest.ini                           # Настройки pytest: маркеры, addopts
├── requirements.txt                     # Зависимости
├── README.md
└── tests/
    ├── __init__.py
    ├── test_first_name_data_driven.py   # TC01–TC15 (параметризованные)
    └── test_first_name_special.py       # TC16–TC18 (DOM / Cookie / JS)
```

---

## Покрытые тест-кейсы

| # | ID pytest | Название чека | Payload |
|---|-----------|---------------|---------|
| 1 | TC01_minimum_value | Minimum value | `A` |
| 2 | TC02_maximum_value | Maximum values | `Abcdefghijklmnopqrstuvwxyzabcd` (30 симв.) |
| 3 | TC03_more_than_maximum | More than maximum values | `Abcdefghijklmnopqrstuvwxyzabcde` (31 симв.) |
| 4 | TC04_average_value | Average value | `John` |
| 5 | TC05_empty_value | Empty value | `""` |
| 6 | TC06_space | Space | `" "` |
| 7 | TC07_space_at_beginning | Space values at the begining | `" John"` |
| 8 | TC08_space_in_middle | Space in the middle | `"John Doe"` |
| 9 | TC09_space_at_end | Space values at the end | `"John "` |
| 10 | TC10_other_chars | Other chars then alphabetic | `John123!` |
| 11 | TC11_non_ascii | Non ASCII | `Иван` |
| 12 | TC12_html_tags | You used html tags | `<b>John</b>` |
| 13 | TC13_xss | Basic XSS | `<script>alert(1)</script>` |
| 14 | TC14_sql_injection | Basic Sql injection | `' OR '1'='1` |
| 15 | TC15_missing_css | Missing css | `detailsoverviewnow.css` |
| 16 | test_tc16_you_looked_at_the_cookie | You looked at the cookie | значение из Cookie |
| 17 | test_tc17_you_looked_at_the_page_source | You looked at the page source | токен из HTML-комментария |
| 18 | test_tc18_you_made_the_user_admin | You made the user admin | JS: value '0'→'1' |

---

## Установка зависимостей

```bash
pip3 install -r requirements.txt --break-system-packages
python3 -m playwright install chromium
```

---

## Запуск тестов

### Все 18 тестов (headless, throttle 200 мс)
```bash
pytest tests/ -v
```

### Только data-driven тесты (TC01–TC15)
```bash
pytest tests/test_first_name_data_driven.py -v
```

### Только специфические тесты (TC16–TC18)
```bash
pytest tests/test_first_name_special.py -v
```

### Запуск одного конкретного теста
```bash
pytest tests/ -v -k "TC13_xss"
```

### Visible browser (headed mode)
```bash
pytest tests/ -v --headed
```

### Увеличить паузу между запросами (двойной throttle)
```bash
pytest tests/ -v --throttle-ms=400
```

### Запуск только помеченных тестов
```bash
pytest tests/ -v -m first_name          # TC01–TC15
pytest tests/ -v -m dom_manipulation    # TC16–TC18
```

---

## Throttling / Защита от бана по IP

> ⚠️ **Сервер блокирует клиентов при > 30 запросов/сек с одного IP.**

Реализована двухуровневая защита:

| Слой | Механизм | Где задаётся |
|------|----------|--------------|
| 1 | `slow_mo=200мс` — задержка после каждого Playwright-вызова | `conftest.py → browser_type_launch_args` |
| 2 | `page.wait_for_timeout(200мс)` — явная пауза перед `page.goto()` | начало каждого теста |

**Итого:** ≥ 400 мс между последовательными HTTP-запросами ≈ **2.5 req/s**
— в 12 раз ниже лимита 30 req/s.

Тесты намеренно запускаются **последовательно** (не параллельно).
Не используйте `pytest-xdist` с несколькими воркерами без дополнительной
настройки throttle.

---

## Описание специфических тестов

### TC16 — You looked at the cookie
Читает все куки домена через `context.cookies()`, фильтрует технические
(`PHPSESSID` и т.п.) и вставляет значение секретной куки в поле First Name.

### TC17 — You looked at the page source
Получает HTML через `page.content()`, ищет скрытый комментарий вида
`<!-- token -->` двумя regex-паттернами (строгий → широкий fallback),
вставляет найденный токен в поле First Name.

### TC18 — You made the user admin
Выполняет JS через `page.evaluate()`, находит скрытый
`input[name="user_right_as_admin"]`, меняет `value` с `'0'` на `'1'`,
снимает атрибуты `hidden`/`disabled`, затем отправляет форму.
