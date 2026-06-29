# Testing Challenges — Playwright UI Test Suite

[![Playwright Tests](https://github.com/shymkovycholeksii/playwright-testing-challenge_01/actions/workflows/tests.yml/badge.svg)](https://github.com/shymkovycholeksii/playwright-testing-challenge_01/actions/workflows/tests.yml)

A suite of automated UI tests in **Python + Playwright** to cover
18 checks for the "First Name" field on the environment
[testingchallenges.thetestingmap.org](http://testingchallenges.thetestingmap.org/index.php).

---

## Project Structure

```
Project_Test_Playwright/
├── pytest.ini                           # pytest settings: markers, addopts
├── requirements.txt                     # Dependencies
├── README.md
└── tests/
    ├── constants.py                     # Centralized constants (URL, selectors, timeouts)
    ├── conftest.py                      # Global pytest-playwright configuration
    ├── test_first_name_data_driven.py   # TC01–TC15 (parameterized)
    └── test_first_name_special.py       # TC16–TC18 (DOM / Cookie / JS)
```

---

## Covered Test Cases

| # | pytest ID | Check Name | Payload |
|---|-----------|---------------|---------|
| 1 | TC01_minimum_value | Minimum value | `A` |
| 2 | TC02_maximum_value | Maximum values | `Abcdefghijklmnopqrstuvwxyzabcd` (30 chars) |
| 3 | TC03_more_than_maximum | More than maximum values | `Abcdefghijklmnopqrstuvwxyzabcde` (31 chars) |
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
| 16 | test_tc16_you_looked_at_the_cookie | You looked at the cookie | Cookie value |
| 17 | test_tc17_you_looked_at_the_page_source | You looked at the page source | token from HTML comment |
| 18 | test_tc18_you_made_the_user_admin | You made the user admin | JS: value '0'→'1' |

---

## Installation

```bash
pip3 install -r requirements.txt --break-system-packages
python3 -m playwright install chromium
```

---

## Running Tests

### All 18 tests (headless, throttle 200 ms)
```bash
pytest tests/ -v
```

### Only data-driven tests (TC01–TC15)
```bash
pytest tests/test_first_name_data_driven.py -v
```

### Only specific tests (TC16–TC18)
```bash
pytest tests/test_first_name_special.py -v
```

### Run one specific test
```bash
pytest tests/ -v -k "TC13_xss"
```

### Visible browser (headed mode)
```bash
pytest tests/ -v --headed
```

### Increase pause between requests (double throttle)
```bash
pytest tests/ -v --throttle-ms=400
```

### Run only marked tests
```bash
pytest tests/ -v -m first_name          # TC01–TC15
pytest tests/ -v -m dom_manipulation    # TC16–TC18
```

---

## Architecture: Centralized Constants

All values used in more than one file are defined in
[`tests/constants.py`](tests/constants.py):

| Constant | Value | Where it is used |
|---|---|---|
| `BASE_URL` | Environment URL | both test files |
| `INTER_TEST_DELAY_MS` | `200` ms | both test files |
| `FIRST_NAME_SELECTOR` | `input[name="firstname"]` | both test files |
| `SUBMIT_SELECTOR` | `input[type="submit"], ...` | both test files |
| `ADMIN_FIELD_SELECTOR` | `input[name="user_right_as_admin"]` | `test_first_name_special.py` |

When expanding the project (new environment, additional fields), it is enough to
edit `constants.py` — all test files will pick up the changes automatically.

---

## CI/CD — GitHub Actions

The project uses **GitHub Actions** to automatically run tests:
[`.github/workflows/tests.yml`](.github/workflows/tests.yml)

### Triggers
- `push` to the `main` branch
- `pull_request` to the `main` branch

### Pipeline Steps

| Step | Action |
|---|---|
| Checkout | Downloads the repository code |
| Set up Python 3.11 | Installs Python with pip caching |
| Install dependencies | `pip install -r requirements.txt` |
| Install Chromium | `playwright install chromium --with-deps` |
| Run tests | `pytest` with `--html=report.html` |
| Upload HTML report | Saves the report for 30 days as an Artifact |

### Viewing the Report

1. Open the **Actions** tab on GitHub
2. Select the desired run
3. At the bottom of the page find **Artifacts** → download `playwright-report-N.zip`
4. Unpack the archive and open `report.html` in a browser

### Reporting (Portfolio)

It uses **`pytest-html`** — generates a portable HTML report with details for each test.
A single `report.html` file contains all results and CSS — without external dependencies.

---

## Throttling / IP Ban Protection

> ⚠️ **The server blocks clients at > 30 requests/sec from a single IP.**

A two-level protection is implemented:

| Layer | Mechanism | Where it is set |
|------|----------|--------------|
| 1 | `slow_mo=200ms` — delay after each Playwright call | `conftest.py → browser_type_launch_args` |
| 2 | `page.wait_for_timeout(200ms)` — explicit pause before `page.goto()` | start of each test |

**Total:** ≥ 400 ms between consecutive HTTP requests ≈ **2.5 req/s**
— 12 times below the 30 req/s limit.

The tests are intentionally run **sequentially** (not in parallel).
Do not use `pytest-xdist` with multiple workers without additional
throttle configuration.

---

## Specific Tests Description

### TC16 — You looked at the cookie
Reads all domain cookies via `context.cookies()`, filters out technical ones
(`PHPSESSID`, etc.) and inputs the secret cookie value into the First Name field.

### TC17 — You looked at the page source
Gets the HTML via `page.content()`, searches for a hidden comment like
`<!-- token -->` with two regex patterns (strict → broad fallback),
inputs the found token into the First Name field.

### TC18 — You made the user admin
Executes JS via `page.evaluate()`, finds the hidden
`input[name="user_right_as_admin"]`, changes `value` from `'0'` to `'1'`,
removes `hidden`/`disabled` attributes, then submits the form.
