# -*- coding: utf-8 -*-
# 爬取sec-wiki的周刊，解析成ts、tag、url、title、root_domain、domain、url_path格式，存储
from github_crawler import get_request,get_github_info
from github_crawler import path
from sqlite import SQLite
import requests
from bs4 import BeautifulSoup
import glob
import re
import logging
import codecs
import tldextract
from urllib.parse import urlparse
import os

def crawl_increse():
    url='https://www.sec-wiki.com/weekly'

    # 判断文件是否已经本地存在
    ex_files=glob.glob('data/html/secwiki_*.html')
    ex_num=[]
    for ex_file in ex_files:
        m=re.search(r'secwiki_(\d+)\.html',ex_file)
        ex_num.append(int(m.group(1)))
    if ex_num:
        max_num=max(ex_num) # 本地最大值
    else:
        max_num=0

    try:
        s=requests.get(url).content
        soup=BeautifulSoup(s,features="lxml")
        week=soup.find('div',class_='issues')
        w_href=week.find('a').get('href')
        new_num=int(w_href[8:])

    except Exception as e:
        logging.info("[request]%s error:%s" %(url,repr(e)))
        return 

    if new_num<=max_num:
        return
    else:
        fnames=crawl_all(max_num,new_num)
        return fnames

def crawl_all(start,end):
    fnames=[]
    for i in range(start+1,end+1):
        url='https://www.sec-wiki.com/weekly/'+str(i)
        if not os.path.exists(path("data/html")):
            os.mkdir(path("data/html"))
        abs_file=path('data/html','secwiki_'+str(i)+'.html')
        try:
            r=requests.get(url)
            if r.status_code==200:
                with codecs.open(abs_file,'wb') as f:
                    f.write(r.content)
                    fnames.append(abs_file)

        except Exception as e:
            logging.info('[request]%s error:%s' %(url,repr(e)))

    return fnames

def parse_single(html):
    soup=BeautifulSoup(html,'lxml')
    # ts
    text=soup.find('blockquote').get_text()
    text=text.strip()
    pattern=re.compile(r'(\d{4})\/(\d{2})\/(\d{2})')
    g=re.search(pattern,text)
    ts=g.group(1)+g.group(2)+g.group(3)

    # tag/title/url/root_domain/path
    for div in soup.find_all("div", class_='single'):
        sts = div.stripped_strings
        tag=next(sts)
        if tag.find("[") != -1:
            tag = tag[1:-1]
        title=next(sts)

        url=div.find('a').get('href')
        ext=tldextract.extract(url)
        root_domain=ext.domain+'.'+ext.suffix
        domain=urlparse(url).netloc
        url_path=urlparse(url).path

        content=(ts,tag,url,title,root_domain,domain,url_path)

        # 从url中提取github和weixin url
        # todo

        yield content

def parse_all(fnames,reparse=False):
    """
    格式化为ts、tag、url、title、root_domain、domain、url_path
    :param reparse:是否重新全部解析
    :return:
    """
    sqldb=SQLite('data/secwiki.db')
    
    # 判断是否重新全部解析
    if reparse:
        fnames=[]
        gen_file=glob.iglob(r'data/html/secwiki_*.html')
        sql='delete from `secwiki`'
        for gfile in gen_file:
            fnames.append(gfile)
        sqldb.execute(sql)

    if fnames is None:
        print('No new secwiki')
        return

    sql='insert into `secwiki` (`ts`,`tag`,`url`,`title`,`root_domain`,`domain`,`url_path`) values(?,?,?,?,?,?,?);'

    for fname in fnames:
        # 判断目标文件本地是否存在
        m=re.search(r'secwiki_(\d+)\.html',fname)
        rname=m.group(1)
        rname=path('data/txt','secwiki_'+rname+'.txt')
        if not os.path.exists(path("data/txt")):
            os.mkdir(path("data/txt"))
        if os.path.exists(rname) and os.path.getsize(rname)>0:
            continue

        # 待统一写入目标文件
        rf=codecs.open(rname,mode='wb')

        # 读本地源文件并解析
        with codecs.open(fname,'rb') as f:
            all_content={}
            #print(fname)
            for content in parse_single(f):
                if content:
                    # 解析完写入目标文件
                    k = content[0] + content[2]
                    all_content[k]=content
                    line = "\t".join(content)
                    rf.write(line.encode()+b'\r\n')
    
            # 批量存入sqlite3
            if all_content:
                sqldb.executemany(sql,all_content.values())

        rf.close()

def secwiki():
    fnames=crawl_increse()
    parse_all(fnames)

if __name__ == '__main__':
    secwiki()
