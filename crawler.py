#!/usr/bin/env python
# coding: utf-8


#爬取百科信息
import urllib
from urllib import request
from urllib import parse
import json
from bs4 import BeautifulSoup
import os
import requests
import re
import codecs
import time
def get_content(url, save_path):
    #打开网页，获取网页内容
    def url_open(url):
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"

        # 代理隧道验证信息
        proxyUser = "HCGO0I870G0184UD"
        proxyPass = "BAD153D4A522D787"

        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host" : proxyHost,
            "port" : proxyPort,
            "user" : proxyUser,
            "pass" : proxyPass,
        }

        # proxy_handler = request.ProxyHandler({
        #     "http"  : proxyMeta,
        #     "https" : proxyMeta,
        # })

        #auth = request.HTTPBasicAuthHandler()
        #opener = request.build_opener(proxy_handler, auth, request.HTTPHandler)

        #opener = request.build_opener(proxy_handler)
        
        #request.install_opener(opener)
        #html = str(request.urlopen(url).read(),'utf-8')
        html = str(request.urlopen(url).read(), 'utf-8')
        time.sleep(1)
        return html

    data = url_open(url)
    soup = BeautifulSoup(data, 'lxml')
    content = soup.body.select('.body-wrapper')[0].select('.content-wrapper')[0].select('.content')[0].select('.main-content')[0]

    tag = content.find(id ='open-tag').find_all(attrs={'class':'taglist'})
    tags = [each.get_text() for each in tag]
    tagschar = list(set([ y for x in tags for y in x]))
    #开始爬取内容
    title = content.select('.lemmaWgt-lemmaTitle')[0].dd.h1.get_text()
    summary = content.select('.lemma-summary')[0].div.get_text().replace('\n','').replace('\xa0','')
    name = content.select('.basic-info')[0].find_all('dt')
    con = content.select('.basic-info')[0].find_all('dd')
    dic = {}
    if len(name) == len(con):
        for (i,j) in zip(name,con):
            dic[i.get_text().replace('\n','').replace('\xa0','')] = j.get_text().replace('\n','').replace('\xa0','')
    basic_info = dic

    index = content.find_all(attrs=re.compile('para'))
    text = {}
    key = ''
    for each in index:
        for cla in each['class']:
            if 'title' in cla and each.get_text() != '':
                key = each.find(attrs = re.compile('h*')).get_text()
        if(key == ''): continue
        else:
            if not key in text: text[key] = []
            else: text[key].append(each.get_text().replace('\n',' ').replace('\xa0','').replace('\u3000',''))

    #保存内容title,summary,basic_info,text         
    result = {}
    result['词条'] = title
    result['概述'] = summary
    result['基本信息'] = basic_info
    result['正文'] = text
    save_title = title+'.json'
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    with codecs.open(os.path.join(save_path, save_title), 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)
        print("词条: " + title + ' save successfull!')
    return data   
if __name__ == '__main__':
    name = parse.quote('模拟电路')
    get_content('https://baike.baidu.com/item/'+name,'test')