
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        url = 'https://www.beqege.com/69985/'
        urls = await get_urls(context=context, url=url)     
        tasks = [get_text(context, url) for url in urls]
        n=10
        sublists = [tasks[i:i+n] for i in range(0, len(tasks), n)]
        results = []
        for i, sublist in enumerate(sublists):
            temps =await asyncio.gather(*sublist)
            results+=temps
            print(f'----{i}----')
     
        await browser.close()
        return results

async def get_text(context, url):
    page = await context.new_page()
    await page.goto(url)
    item = await page.query_selector('//*[@id="content"]')
    text = await item.text_content()  
    await page.close()
    return text

async def get_urls(context, url):
    page = await context.new_page()
    await page.goto(url)
    element = await page.query_selector_all ('//*[@id="list"]/dl/dd/a') 
    urls = []
    for item in element:
        temp = await item.get_attribute('href')
        temp = 'https://www.beqege.com'+temp
        urls.append(temp)
    print(len(urls),urls[0])
    await page.close()
    return urls

if __name__ == '__main__':
    ret = asyncio.run(main()) 
    with open('aaaa.txt', 'w') as file:
        # 将每行文本写入文件
        for line in ret:
            file.write(line + '\n')

    