from playwright.sync_api import Playwright, sync_playwright
import asyncio


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

  
    url = 'https://www.beqege.com/cover/76/76421.jpg'
    page.goto(url)
    image_data = page.screenshot()

    with open('image.jpg', 'wb') as f:
        f.write(image_data)

    browser.close()


import asyncio
from playwright.async_api import async_playwright, Playwright
import sqlite3

async def getImage(context,url): 
        page = await context.new_page()
        await page.goto(url)
        await page.screenshot(path=f"image/{url.split('/')[-1]}")
        await page.close()


async def main():
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    sql = 'SELECT image_url FROM novels'
    cursor.execute(sql)
    rows = cursor.fetchall() 
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(viewport={'width': 120, 'height': 150})
        tasks = [getImage(context,row[0])  for row in rows]
        await asyncio.gather(*tasks)
        await browser.close()

asyncio.run(main())