from playwright.sync_api import Playwright, sync_playwright
import time

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto('https://www.beqege.com/')
    print(page.title())