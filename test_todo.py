"""Playwright E2E tests for the Todo app."""
import sys
from playwright.sync_api import sync_playwright

URL = 'http://localhost:5000'
passed, failed = [], []

def check(name, cond, detail=''):
    if cond:
        passed.append(name)
        print(f'  PASS: {name}')
    else:
        failed.append(name)
        print(f'  FAIL: {name}  {detail}')

def count(page): return page.locator('.item').count()

def wait_count(page, n, timeout=3000):
    page.wait_for_function(f'document.querySelectorAll(".item").length === {n}', timeout=timeout)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({'width': 1280, 'height': 800})
    page.goto(URL)
    page.wait_for_selector('.card')

    print('\n=== Initial State ===')
    check('page loads', 'Todo' in page.title())
    check('empty state', page.locator('.empty').is_visible())
    check('no offline banner', page.locator('#offlineBanner').is_hidden())
    check('date picker exists', page.locator('#dueDateInput').is_visible())
    check('count 0', '0 items' in page.locator('#count').text_content())

    print('\n=== Add Tasks ===')
    page.fill('#input', 'Buy groceries')
    page.click('#addBtn')
    wait_count(page, 1)
    check('first todo added', count(page) == 1, str(count(page)))
    check('first todo text', page.locator('.item').first.locator('.text').text_content() == 'Buy groceries')

    page.fill('#input', 'Walk the dog')
    page.fill('#dueDateInput', '2026-07-20')
    page.locator('#input').focus()
    page.keyboard.press('Enter')
    wait_count(page, 2)
    check('second with due date', count(page) == 2, str(count(page)))
    due_spans = page.locator('.date.due')
    check('due date badge visible', due_spans.count() >= 1, str(due_spans.count()))

    page.fill('#input', 'Read a book')
    page.wait_for_timeout(100)
    page.click('#addBtn')
    wait_count(page, 3)
    check('third todo', count(page) == 3, str(count(page)))

    print('\n=== Toggle ===')
    page.locator('.checkbox').first.click()
    page.wait_for_timeout(400)
    check('first completed', page.locator('.text.done').count() == 1)

    print('\n=== Filter ===')
    page.locator('button[data-filter="active"]').click()
    page.wait_for_timeout(200)
    check('active filter 2', count(page) == 2, str(count(page)))

    page.locator('button[data-filter="completed"]').click()
    page.wait_for_timeout(200)
    check('completed filter 1', count(page) == 1, str(count(page)))

    page.locator('button[data-filter="all"]').click()
    page.wait_for_timeout(200)
    check('all filter 3', count(page) == 3, str(count(page)))

    print('\n=== Clear Completed ===')
    page.locator('.checkbox').first.click()
    page.wait_for_timeout(200)
    page.locator('.checkbox').nth(1).click()
    page.wait_for_timeout(400)
    page.locator('#clearBtn').click()
    page.wait_for_timeout(400)
    check('clear completed: 2 remain', count(page) == 2, str(count(page)))

    print('\n=== Delete & Undo ===')
    page.locator('.del-btn').first.click()
    page.wait_for_timeout(500)
    check('delete: 1 remains', count(page) == 1, str(count(page)))
    check('undo toast', page.locator('.toast-undo').is_visible())
    page.locator('.toast-undo').click()
    page.wait_for_timeout(500)
    check('undo restores: 2', count(page) == 2, str(count(page)))

    print('\n=== Offline Banner ===')
    check('no offline banner', page.locator('#offlineBanner').is_hidden())

    print('\n=== API ===')
    res = page.evaluate('''async () => {
      const r = await fetch('/api/todos');
      const d = await r.json();
      return d.length;
    }''')
    check('API returns correct count', res == 2, str(res))

    print('\n=== Persistence ===')
    page.reload()
    page.wait_for_selector('.card')
    page.wait_for_timeout(500)
    check('todos persist', count(page) == 2, str(count(page)))

    print(f'\n{"="*40}')
    print(f'Results: {len(passed)} passed, {len(failed)} failed')
    if failed: print(f'Failed: {", ".join(failed)}')
    print(f'{"="*40}')
    browser.close()
    sys.exit(1 if failed else 0)
