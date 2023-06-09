import uvicorn
from fastapi import FastAPI
import requests
from lxml import etree
import random
import os
import time
from starlette.responses import FileResponse
import sqlite3
from  bookBeqegeCom import *
import edge_tts
import multiprocessing
import shutil

async def edgeTTS(text:str,outFile,voice= 'Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoNeural)') :
    communicate = edge_tts.Communicate(text, voice) 
    await communicate.save(outFile)



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

#实现了https://shaoyang.fun/contents/?id=10&bookId=251
@app.get("/contents/")
async def catalogue(id,bookId):
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM book{bookId} WHERE id BETWEEN ? AND ?', (int(id), int(id)+20))
    rows = cursor.fetchall()
    # 输出结果
    contents = []
    for row in rows:
        temp = {'id':row[0],'chapter':row[1],'content':row[2]}
        contents.append(temp) 
    conn.close()
    return  contents 


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
async def bookList():
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
    conn.close()
    if rows:        
        return rows[0][0]
    return 
    url = await searchNovel(bookName)
    if url:
        id = await downloadNovel(url=url,n=5)
        return id
    

#
@app.get("/classifyNovel/")
async def classifyNovel(name):
    if name=='新书':
        pass
    ret = await bookList()
    return  ret

@app.get("/register/{name}/{phone}/{password}/")
async def register(name,phone,password):
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()  
    try: 
        cursor.execute("INSERT INTO users (name, phone, password) VALUES (?, ?, ?)", (name, phone, password))
    except:
        conn.commit()
        conn.close()
        return 0  
    conn.commit()
    conn.close()
    return 1
  

@app.get("/getUserInfo/")
async def getUserInfo(phone,password):
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    sql = f"SELECT * FROM users WHERE phone={phone};"
    # 执行 SQL 语句并获取结果
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    # 输出结果
    if rows:
        if password==rows[0][6]:
            return {'id':rows[0][0],'name':rows[0][1]}
        return 0
    return -1    
    
@app.get("/addBook/{bookId}/{userId}/{chapter}/{isAdd}/")
async def addBook(bookId,userId,chapter,isAdd):
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    # 执行 SQL 语句并获取结果
    if isAdd=='1':     
        cursor.execute("UPDATE favorites SET chapter = ? WHERE  user_id=? AND novel_id=?", (int(chapter),int(userId),int(bookId)))
        if cursor.rowcount==0:
            cursor.execute('INSERT INTO favorites (user_id,novel_id,chapter) VALUES (?,?,?)',(int(userId),int(bookId),int(chapter)))
    else:
        cursor.execute("DELETE FROM favorites WHERE user_id=? AND novel_id=?", (int(userId), int(bookId)))
    ret  = cursor.rowcount
    conn.commit()
    conn.close()
    return ret
    

@app.get("/bookshelf/")
async def bookshelf(id):
    conn = sqlite3.connect('novels.db')
    cursor = conn.cursor()
    sql = f"SELECT novel_id, chapter FROM favorites WHERE user_id={id};"
    # 执行 SQL 语句并获取结果
    cursor.execute(sql)
    rows = cursor.fetchall()
    books = []
    print(f'-----{len(rows)}-----')
    for row in rows: 
        sql = f"SELECT id, title, author,image_url, content FROM novels WHERE id={row[0]}"
        # 执行 SQL 语句并获取结果
        cursor.execute(sql)
        bookRow = cursor.fetchall()[0]
        # 输出结果      
        result = {
            "id": bookRow[0],
            "title": bookRow[1],
            "author": bookRow[2],
            "image_url": bookRow[3],
            "content": bookRow[4],
            "chapter":row[1]
        }
        books.append(result) 
    conn.close()
    return books


def worker(phone,bookId,chapterId,id,texts):
    for i, item in enumerate(texts):
        for j,text in enumerate(item):
            outFile =  f'{phone}/{bookId}{chapterId}{id+i}{j}.wav'            
            asyncio.run(edgeTTS(text,outFile))
    
def worker1(phone,bookId,chapterId,id,texts):
    for i, item in enumerate(texts):
        for j,text in enumerate(item):
            outFile =  f'{phone}/{bookId}{chapterId}{id+i}{j+2}.wav'            
            asyncio.run(edgeTTS(text,outFile))

@app.get("/getVoice/")
async def getVoice(bookId,chapterId,id,texts): 
    path = '.'
    for file in os.listdir(path):
        if file.endswith(".wav"):
            os.remove(os.path.join(path, file))    
    textlist = eval(texts)
    id = int(id)
    text = '\n'.join(textlist[id-1]).replace('&emsp;','') 
    outFile = outFile = f'{bookId}{chapterId}{id}.wav'
    p = multiprocessing.Process(target=worker,args=(id+1,textlist[id:]))
    p.start()
    await edgeTTS(text,outFile) 
    return 


from pydantic import BaseModel
class Item(BaseModel):
    phone:str
    bookId:int
    chapterId:int
    id: int
    texts: list

@app.post("/postVoice/")
async def postVoice(item:Item): 
    item_dict = item.dict() 
    if os.path.exists(f'{item_dict["phone"]}'):
        shutil.rmtree(f'{item_dict["phone"]}')
    os.mkdir(f'{item_dict["phone"]}') 
    textlist = item_dict['texts']  
    id = item_dict['id']  
    p1 = multiprocessing.Process(target=worker1,args=(item_dict["phone"],item_dict["bookId"],item_dict["chapterId"],id,[textlist[id-1][2:]]))
    p1.start()
    for i,text in enumerate(textlist[id-1][:2]):        
        outFile = f'{item_dict["phone"]}/{item_dict["bookId"]}{item_dict["chapterId"]}{id}{i}.wav'
        await edgeTTS(text,outFile)  
    p = multiprocessing.Process(target=worker,args=(item_dict["phone"],item_dict["bookId"],item_dict["chapterId"],id+1,textlist[id:]))
    p.start()  
    return 'ok'


class testpostItem(BaseModel):    
    bookId:int
    chapterId:int    
@app.post("/testpost/")
async def testpost(item:testpostItem): 
    item_dict = item.dict() 
    print(item_dict)
    return 'aaaa'


#实现了下载文件
@app.get("/voice/{phone}/{name}/")
async def voice(phone,name):
    # file：文件路径
    return FileResponse(f'{phone}/{name}')


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=443, ssl_keyfile="fun.key", ssl_certfile="fun.pem")

    