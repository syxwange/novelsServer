import uvicorn
from fastapi import FastAPI
import requests
from lxml import etree
import random
import json
import time
from starlette.responses import FileResponse
import sqlite3
from  bookBeqegeCom import *

app = FastAPI()
# Define your FastAPI routes here
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/swiper")
async def getSwiper():
    url = 'https://www.qidian.com/book/coverrec/'
    response = requests.get(url)
    html = response.content.decode('utf-8')
    selector = etree.HTML(html)
    node = selector.xpath('/html/body/div/div[3]/div[1]/ul/li')
    swipes= []
    for item in random.sample(node, 4):
        temp = {}
        names = item.xpath('./div[2]/strong/h2/a/text()')
        srcs = item.xpath('./div[1]/a/img/@src')
        temp['name'] = names[0]
        temp['src'] = srcs[0]
        swipes.append(temp)
    return swipes

#实现了https://shaoyang.fun/catalogue/?name=aaaa
@app.get("/catalogue/")
async def catalogue(id):
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    sql = f"SELECT * FROM book{id} "
    # 执行 SQL 语句并获取结果
    cursor.execute(sql)
    rows = cursor.fetchall()
    # 输出结果
    results = []
    for row in rows:
        result = {
            "id": row[0],
            "chapter": row[1], 
        }
        results.append(result)
    conn.close()
    return results

#实现了https://shaoyang.fun/content/?id=10&bookId=251
@app.get("/content/")
async def catalogue(id,bookId):
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    sql = f"SELECT * FROM book{bookId} WHERE id={id};"
    # 执行 SQL 语句并获取结果
    cursor.execute(sql)
    rows = cursor.fetchall()
    # 输出结果
    results =rows[0][2]
    conn.close()
    return results

#实现了下载文件
@app.get("/download/")
async def downloadFile():
    # file：文件路径
    return FileResponse("/root/wg/favicon1.ico", filename="favicon1.ico")

#实现https://shaoyang.fun/image/001.png 打开一张图片
#image/jpeg：JPEG图像文件  image/png：PNG图像文件  image/gif：GIF图像文件 
#text/html：HTML文件  text/plain：纯文本文件  application/json：JSON文件
#application/pdf：PDF文件  application/zip：ZIP压缩文件
@app.get("/image/{imageName}")
async def getImage(imageName):
    return FileResponse(imageName, media_type="image/png")


@app.get("/bookList")
async def getSwiper():
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()

    # 编写 SQL 语句，从 novels 表中随机选择 10 条记录
    sql = "SELECT id,title, author,image_url, content FROM novels ORDER BY RANDOM() LIMIT 15"
    # 执行 SQL 语句并获取结果
    cursor.execute(sql)
    rows = cursor.fetchall()

    # 输出结果
    results = []
    for row in rows:
        result = {
            "id": row[0],
            "title": row[1],
            "author": row[2],
            "image_url": row[3],
            "content": row[4]
        }
        results.append(result)
    conn.close()
    return results


@app.get("/search/{bookName}")
async def searchBook(bookName):
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    sql = f"SELECT id FROM novels WHERE title='{bookName}';"
    # 执行 SQL 语句并获取结果
    cursor.execute(sql)
    rows = cursor.fetchall()
    if rows:
        return rows[0][0]
    url = await searchNovel(bookName)
    if url:
        id = await downloadNovel(url=url,n=5)
        return id
    


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile="fun.key", ssl_certfile="fun.pem")

    