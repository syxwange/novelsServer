
#
#'https://www.mayiwxw.com'
# 'http://www.42zw.la'
#



import requests
from lxml import etree
import lxml
import sqlite3
import logging

logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG,filename='novels.log')


def searchInMayiwxw(name):
    netUrl = 'https://www.mayiwxw.com'
    headers = {
        'Origin': 'https://www.mayiwxw.com',
        'Referer': 'https://www.mayiwxw.com/10_10157/index.html',    
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50',
    }

    data = {
        'searchkey': name,
        'searchtype': 'articlename',
    }

    html = requests.post('https://www.mayiwxw.com/modules/article/search.php',  headers=headers, data=data).text
    try:
        bookUrl = etree.HTML(html).xpath('//*[@id="nr"]/td[1]/a/@href')[0]
        return netUrl+bookUrl,netUrl
    except:
        logging.info(html)   
        return 
    
def searchIn42zw(name):
    netUrl = 'http://www.42zw.la'

    html =  requests.get(url=f'http://www.42zw.la/search?keyword={name}').text
    root  = etree.HTML(html)
    try:
        bookUrl = netUrl+root.xpath('//*[@id="main"]/div/ul/li[2]/span[2]/a/@href')[0]
        return bookUrl,netUrl
    except:
        logging.info(html)   
        return 
    


#查找小说是否在数据库中，有返回小说id和章节数，否则创建小说条目，返回新建小说id,章节数0     
def checkNovelUpdate(name:str,author,image_url:str,content:str,category='玄幻'):
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


def downloadNovel(name='半仙',n=0):
    bookUrl,netUrl = searchInMayiwxw(name)    
    if not bookUrl:
        bookUrl,netUrl = searchIn42zw(name)   
    if not bookUrl:
        return
    html =  requests.get(url=bookUrl).text

    id ,nCount= checkNovelUpdate(category=category,name=name,author=author,image_url=src,content=intro,ncount=len(chapters)) 
    
    root  = etree.HTML(html).xpath('//*[@id="list"]')
    dt = root[0].xpath('//*[@id="list"]/dl/dt[2]')[0]

    # 获取该元素后面的所有兄弟节点
    siblings = dt.xpath('following-sibling::node()')
    print(len(siblings))
    urls = []
    chapters = []
    for ietm in siblings:
        if type(ietm)==lxml.etree._Element:
            tempUrl = netUrl+ ietm.xpath('./a/@href')[0]
            chapter = ietm.xpath('./a/text()')[0].strip()   
            urls.append(tempUrl)
            chapters.append(chapter)
    if nCount==len(urls):        
        logging.info(f'《{name}》不用更新')           
        return id
    
    if n==0:
        nCount = len(urls)
        i=0
        while i<nCount:
            url,chapter =urls[i],chapters[i]
            tempText = requests.get(url=url).text
            tempNode = etree.HTML(tempText)          
            try:
                content = tempNode.xpath('//*[@id="content"]')[0]
                
            except:
                logging.info(tempText)
                continue
            text = content.xpath('string(.)')
            clean_text = "\n".join([line.lstrip() for line in text.split("\n") if line.strip() and 'ｈｔｔｐ://' not in line][2:])
       
            i+=i
        return 

    texts = []
    for url,chapter in zip(urls,chapters)[:n]:
        tempText = requests.get(url=url).text
        tempNode = etree.HTML(tempText)          
        try:
            content = tempNode.xpath('//*[@id="content"]')[0]
        except:
            logging.info(tempText)
        text = content.xpath('string(.)')
        clean_text = "\n".join([line.lstrip() for line in text.split("\n") if line.strip() and 'ｈｔｔｐ://' not in line][2:])
        texts.append(clean_text)
 
    return texts