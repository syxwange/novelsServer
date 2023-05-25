
#
#'https://www.beqege.com'这个网站下载小说
#http://www.42zw.la/
#


import asyncio
from playwright.async_api import async_playwright
import time
import sqlite3
import logging

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG,filename='novels.log')

pageurls = ['https://www.beqege.com/class1/',  'https://www.beqege.com/class2/',
        'https://www.beqege.com/class3/',   'https://www.beqege.com/class4/',
        'https://www.beqege.com/class5/',   'https://www.beqege.com/class6/',
        'https://www.beqege.com/class7/',   'https://www.beqege.com/class8/'
        ]  

#笔趣阁网站首页搜索name小说。有就返回url没有返回null
async def searchNovel(name:str):
    async with async_playwright() as p:      
        browser = await p.firefox.launch()        
        page = await browser.new_page()
        url = 'https://www.beqege.com'
        await page.goto(url)  
        # //*[@id="keyword"]    搜索文本框
        await page.fill('//*[@id="keyword"]', name)
        # //*[@id="sform"]/div/span/input    检素按钮
        await page.click('//*[@id="sform"]/div/span/input')  
        try:
            element =  page.get_by_text(name) 
            await element.click()
            ret = page.url 
        except:
            ret = ''
        finally:
            await browser.close()
            return ret

#查找小说是否在数据库中，有返回小说id和章节数，否则创建小说条目，返回新建小说id,章节数0     
def checkNovelUpdate(category:str,name:str,author,image_url:str,content:str,ncount):
    conn = sqlite3.connect('novels.db')
    c = conn.cursor()
    c.execute(f"SELECT id FROM novels WHERE title = '{name}'")
    novelId = c.fetchone()  
    if novelId:
        novelId = novelId[0]    
        c.execute(f'SELECT COUNT(*) FROM book{novelId}')
        rowCount = c.fetchone()[0]      
    else:
        
        c.execute("INSERT INTO novels (title, author,  category,image_url,content) VALUES (?, ?, ?, ?,?)", (name, author,category, image_url,content))
        novelId = c.lastrowid 
        logging.info(f'新建小说《{name}》id：{novelId}。')
        bookName = f'book{novelId}'
        c.execute(f'''CREATE TABLE {bookName} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter VARCHAR(50) NOT NULL,
            novelText TEXT NOT NULL );
        ''')
        rowCount = 0       
    conn.commit()
    conn.close()
    return novelId,rowCount

#下载url的小说主体，返回小说id,章节名称列表和章节内容列表
async def downloadNovel(url:str,n:int=200):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()       
        name,category,author,intro,src,urls,chapters = await getChapterUrls(context=context, url=url)
        #判断小说是否存在，如存在是否更新         
        id ,nCount= checkNovelUpdate(category=category,name=name,author=author,image_url=src,content=intro,ncount=len(chapters)) 
        if nCount==len(urls):
            await browser.close() 
            logging.info(f'《{name}》不用更新')           
            return id
        tasks = [getText(context, url) for url in urls[nCount:]] 
        sublists = [tasks[i:i+n] for i in range(0, len(tasks), n)]
        chapters = chapters[nCount:]
        sublistsChapters = [chapters[i:i+n] for i in range(0, len(chapters), n)]
        # texts = []
        conn = sqlite3.connect('novels.db')
        c = conn.cursor() 
        for sublist , sublistsChapter in zip(sublists,sublistsChapters):
            temps =await asyncio.gather(*sublist)         
            for chapter,text in zip(sublistsChapter,temps):
                c.execute(f'INSERT INTO book{id} (chapter,novelText) VALUES (?,?)',(chapter,text))
            conn.commit()
            print(f'====finshed{len(temps)}=====')
        conn.close()
        await browser.close()
        logging.info(f'《{name}》更新{len(chapters)}章节') 
        return id

#得到小说章节的文字，主要用于协程处理
async def getText(context, url):
    page = await context.new_page()
    await page.goto(url)
    item = await page.query_selector('//*[@id="content"]')
    text = await item.text_content()  
    await page.close()
    return text

#通过url得到小说名字，类别，作者，简介，图片src，章节url列表，章节名称列表
async def getChapterUrls(context, url):
    page = await context.new_page()
    await page.goto(url)
    # //*[@id="info"]/h1 书名
    name = await page.text_content('//*[@id="info"]/h1')
    # //*[@id="main"]/div[1]/div[1]/a[2] 类别
    category = await page.text_content('//*[@id="main"]/div[1]/div[1]/a[2]')
    # //*[@id="info"]/p[1]  作者
    author = await page.text_content('//*[@id="info"]/p[1]')
    author = author.split('：')[1]   
    # //*[@id="intro"]/p[1] 小说简介
    intro = await page.text_content('//*[@id="intro"]/p[1]')
    # //*[@id="fmimg"]/img/@src 图片src  //*[@id="fmimg"]/img  
    src = await page.get_attribute('//*[@id="fmimg"]/img','data-original') 
    if src:
        src = 'https://www.beqege.com'+src
    elements = await page.query_selector_all ('//*[@id="list"]/dl/dd/a') 
    urls = []
    chapters = []
    for item in elements:
        temp = await item.get_attribute('href')        
        temp = 'https://www.beqege.com'+temp
        chapter = await item.text_content()
        urls.append(temp)
        chapters.append(chapter)    
    await page.close()
    return name,category,author,intro,src,urls,chapters

#得到笔趣阁分类页面的所有小说URL和名字
async def getNovelUrls(context, url):
    page = await context.new_page()
    await page.goto(url)
   
    # //*[@id="newscontent"]/div[1]/ul/li/span[1]/a  得到左边小说最近更新列表
    elements = await page.query_selector_all ('//*[@id="newscontent"]/div[1]/ul/li/span[1]/a') 
    urls = []
    names = []
    for item in elements:
        temp = await item.get_attribute('href')        
        temp = 'https://www.beqege.com'+temp
        name = await item.text_content()
        urls.append(temp)
        names.append(name)    

    # //*[@id="newscontent"]/div[2]/ul/li/span[2]/a  得到右边小说热门榜
    elements = await page.query_selector_all ('//*[@id="newscontent"]/div[2]/ul/li/span[2]/a') 
    for item in elements:
        name = await item.text_content()
        if name in names:
            continue
        temp = await item.get_attribute('href')        
        temp = 'https://www.beqege.com'+temp        
        urls.append(temp)
        names.append(name)  
    await page.close()
    return urls,names

#得到笔趣阁所有页面的所有小说URL和名字
async def getAllUrls(pageurlList=pageurls):

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context() 
        urls,names=[],[]
        for url in pageurlList:
            tempUrl,tempName = await getNovelUrls(context=context, url=url)
            urls+=tempUrl
            names+=tempName
      
        await browser.close()
        return urls,names

#笔趣阁网站首页搜索name小说。并下载放到数据库中
async def getNovelByName(name:str):
    url = await searchNovel(name=name)
    if not url:
        print(f'没有找到《{name}》小说')
        return
    novelId,chapters,texts =  await downloadNovel(url=url)
    conn = sqlite3.connect('novels.db')
    c = conn.cursor() 
    for chapter,text in zip(chapters,texts):
        c.execute(f'INSERT INTO book{novelId} (chapter,novelText) VALUES (?,?)',(chapter,text))
    
    conn.commit()
    conn.close()
        
async def update(n=200):
    logging.info(f'---- 开始更新小说。---')  
    start =0
    urls ,names= await getAllUrls()  
    logging.info(f'准备更新{len(urls)}本小说。')  
    while start<len(urls):  
        url = urls[start]
        try:
            id =  await downloadNovel(url=url,n=n)          
 
            start+=1      
        except Exception as e:
            logging.info(f'==={names[start]}出现异常===')
            time.sleep(30)  

async def bak():
    pass

if __name__ == '__main__':
    asyncio.run(update(10))


    