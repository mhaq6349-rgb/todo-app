"""Playwright E2E tests for the Todo app."""
import sys
from playwright.sync_api import sync_playwright

URL = 'http://localhost:5000'
passed = []
failed = []

def check(name, cond, detail=''):
    if cond:
        passed.append(name)
        print(f'  PASS: {name}')
    else:
        failed.append(name)
        print(f'  FAIL: {name}  {detail}')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({'width': 1280, 'height': 800})
    page.goto(URL)
    page.wait_for_selector('.card')

    print('\n=== Initial State ===')
    check('page loads', 'Todo' in page.title())
    check('empty state shown', page.locator('.empty').is_visible())
    check('count = 0 items', '0 items' in page.locator('#count').text_content())
    check('remaining = 0 left', '0 left' in page.locator('#remaining').text_content())

    print('\n=== Add Tasks ===')
    input_el = page.locator('#input')
    add_btn = page.locator('#addBtn')
    input_el.fill('Buy groceries')
    add_btn.click()
    page.wait_for_timeout(400)
    items = page.locator('.item')
    check('first todo added', items.count() == 1, str(items.count()))
    if items.count() > 0:
        check('first todo text', items.first.locator('.text').text_content() == 'Buy groceries')

    input_el.fill('Walk the dog')
    page.keyboard.press('Enter')
    page.wait_for_timeout(400)
    check('second todo via Enter', page.locator('.item').count() == 2, str(page.locator('.item').count()))

    input_el.fill('Read a book')
    add_btn.click()
    page.wait_for_timeout(400)
    check('third todo', page.locator('.item').count() == 3, str(page.locator('.item').count()))
    check('count = 3 items', '3 items' in page.locator('#count').text_content())

    print('\n=== Toggle ===')
    page.locator('.checkbox').first.click()
    page.wait_for_timeout(400)
    check('first item completed', page.locator('.text.done').count() == 1, str(page.locator('.text.done').count()))

    page.locator('.checkbox').nth(1).click()
    page.wait_for_timeout(500)
    check('second item completed', page.locator('.text.done').count() == 2, str(page.locator('.text.done').count()))
    page.wait_for_timeout(200)
    check('remaining = 1 left', '1 left' in page.locator('#remaining').text_content())

    page.locator('.checkbox').nth(1).click()
    page.wait_for_timeout(400)
    check('second item uncompleted', page.locator('.text.done').count() == 1, str(page.locator('.text.done').count()))
    check('clear done button shows', page.locator('#clearBtn').is_visible())

    print('\n=== Filter ===')
    page.locator('button[data-filter="active"]').click()
    page.wait_for_timeout(200)
    check('active filter 2 items', page.locator('.item').count() == 2, str(page.locator('.item').count()))

    page.locator('button[data-filter="completed"]').click()
    page.wait_for_timeout(200)
    check('completed filter 1 item', page.locator('.item').count() == 1, str(page.locator('.item').count()))

    page.locator('button[data-filter="all"]').click()
    page.wait_for_timeout(200)
    check('all filter 3 items', page.locator('.item').count() == 3, str(page.locator('.item').count()))

    print('\n=== Clear Completed ===')
    page.locator('#clearBtn').click()
    page.wait_for_timeout(400)
    check('clear completed: 2 items', page.locator('.item').count() == 2, str(page.locator('.item').count()))
    check('remaining = 2 left', '2 left' in page.locator('#remaining').text_content())

    print('\n=== Edit ===')
    page.locator('.edit-btn').first.click()
    page.wait_for_timeout(200)
    check('edit mode', page.locator('.text-edit').is_visible())
    page.locator('.text-edit').fill('Buy organic groceries')
    page.locator('[data-save]').click()
    page.wait_for_timeout(300)
    check('edit saved', page.locator('.item').first.locator('.text').text_content() == 'Buy organic groceries')

    print('\n=== Escape cancels edit ===')
    page.locator('.edit-btn').first.click()
    page.wait_for_timeout(200)
    page.keyboard.press('Escape')
    page.wait_for_timeout(200)
    check('escape cancels', page.locator('.text-edit').count() == 0, str(page.locator('.text-edit').count()))

    print('\n=== Delete & Undo ===')
    page.locator('.del-btn').first.click()
    page.wait_for_timeout(500)
    check('delete: 1 remains', page.locator('.item').count() == 1, str(page.locator('.item').count()))
    check('undo toast', page.locator('.toast-undo').is_visible())
    page.locator('.toast-undo').click()
    page.wait_for_timeout(500)
    check('undo restores', page.locator('.item').count() == 2, str(page.locator('.item').count()))

    print('\n=== Timestamps ===')
    check('timestamps visible', page.locator('.date').count() > 0, str(page.locator('.date').count()))

    print('\n=== Empty input ===')
    input_el.focus()
    add_btn.click()
    page.wait_for_timeout(200)
    check('empty input ignored', page.locator('.item').count() == 2, str(page.locator('.item').count()))

    print('\n=== Persistence ===')
    page.reload()
    page.wait_for_selector('.card')
    page.wait_for_timeout(500)
    check('todos persist', page.locator('.item').count() == 2, str(page.locator('.item').count()))

    print(f'\n{"="*40}')
    print(f'Results: {len(passed)} passed, {len(failed)} failed')
    if failed:
        print(f'Failed: {", ".join(failed)}')
    print(f'{"="*40}')
    browser.close()
    sys.exit(1 if failed else 0)
