# 深度爬取百度百科
import urllib.request
from bs4 import BeautifulSoup
import re
import threading  
import requests
import time 
from crawler import *

g_mutex = threading.Condition()  
g_pages = [] #从中解析所有url链接  
g_queueURL = [] #等待爬取的url链接列表  
g_existURL = [] #已经爬取过的url链接列表    
g_writecount = 0 #找到的链接数

class Crawler:  
    def __init__(self,url,threadnum,save_path):   
        self.url=url  
        self.threadnum=threadnum  
        self.threadpool=[]   
        self.save_path = save_path
    def craw(self):  #爬虫的控制大脑，包括爬取网页，更新队列
        global g_queueURL  
        g_queueURL.append(url)
        depth=1
        while(depth < 3):    
            print ('Searching depth ',depth,'...\n')  
            self.downloadAll()  
            self.updateQueueURL()
            g_pages = []
            depth += 1  

    def downloadAll(self): #调用多线程爬虫，在小于线程最大值和没爬完队列之前，会增加线程
        global g_queueURL    
        i=0  
        while i<len(g_queueURL):  
            j=0  
            while j<self.threadnum and i+j < len(g_queueURL):    
                threadresult = self.download(g_queueURL[i+j], j, self.save_path)    
                j+=1  
            i += j  
            for thread in self.threadpool:  
                thread.join(30)  
            threadpool=[]  
        g_queueURL=[]  

    def download(self,url,tid,save_path): #调用多线程爬虫 
        crawthread=CrawlerThread(url,tid,save_path)  
        self.threadpool.append(crawthread)  
        crawthread.start()  

    def updateQueueURL(self): #完成一个深度的爬虫之后，更新队列
        global g_queueURL  
        global g_existURL  
        newUrlList=[]  
        for content in g_pages:  
            newUrlList+=self.getUrl(content)  
        g_queueURL=list(set(newUrlList)-set(g_existURL))    
 
    def getUrl(self,content): #从获取的网页中解析url 
        global g_writecount  
        pool = []
        soup = BeautifulSoup(content,"html.parser").body.select('.body-wrapper')[0].select('.content-wrapper')[0].select('.content')[0].select('.main-content')[0]
        for each in soup.find_all(href=re.compile('item')):
            href = ''.join(["http://baike.baidu.com",each["href"]])
            g_writecount += 1
            pool.append(href)
        pool = list(set(pool))
        return pool


class CrawlerThread(threading.Thread): #爬虫线程
    def __init__(self,url,tid,save_path):  
        threading.Thread.__init__(self)  
        self.url=url  
        self.tid=tid 
        self.save_path = save_path
    def run(self):  
        global g_mutex    
        try:
            print (self.tid, "crawl ", self.url)
            html = get_content(self.url, self.save_path)
            

        except Exception as e: 
            g_mutex.acquire()  
            g_existURL.append(self.url)   
            g_mutex.release()  
            print ('Failed downloading and saving',self.url)
            print (e)
            return None

        g_mutex.acquire()  
        g_pages.append(html)  
        g_existURL.append(self.url)  
        g_mutex.release()

if __name__ == "__main__":
    i = 0
    urlList = ['https://baike.baidu.com/item/%E9%AB%98%E9%A2%91%E5%B0%8F%E4%BF%A1%E5%8F%B7%E6%94%BE%E5%A4%A7%E5%99%A8',
                'https://baike.baidu.com/item/%E6%AD%A3%E5%BC%A6%E6%B3%A2%E6%8C%AF%E8%8D%A1%E5%99%A8',
                'https://baike.baidu.com/item/%E8%B0%83%E5%B9%85/2482832',
                'https://baike.baidu.com/item/%E5%8D%8A%E5%AF%BC%E4%BD%93',
                'https://baike.baidu.com/item/%E6%95%B4%E6%B5%81%E7%94%B5%E8%B7%AF',
                'https://baike.baidu.com/item/%E6%BB%A4%E6%B3%A2%E7%94%B5%E8%B7%AF',
                'https://baike.baidu.com/item/%E8%BF%90%E7%AE%97%E6%94%BE%E5%A4%A7%E5%99%A8',
                'https://baike.baidu.com/item/%E7%94%B5%E8%B7%AF/33197',
                'https://baike.baidu.com/item/%E6%A8%A1%E6%8B%9F%E7%94%B5%E8%B7%AF/5896']
    for url in urlList:
        i+=1
        print('爬取第%s词条'%i)
        threadnum = 5
        crawler = Crawler(url,threadnum,'test')  
        crawler.craw()

# url = 'https://baike.baidu.com/item/%E7%BD%91%E7%BB%9C%E7%88%AC%E8%99%AB'
# item = findItem(url, 1)
# print(len(item))
# it = list(set(item))
# print(len(it))
    