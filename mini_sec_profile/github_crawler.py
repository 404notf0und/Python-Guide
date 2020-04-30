import os
import codecs
import re
import hashlib
import requests
import logging
from bs4 import BeautifulSoup
import datetime

def path(*paths):
    """
    计算目录及文件的绝对路径
    :param *paths:
    :return:
    """
    dir_name=os.path.dirname(os.path.realpath(__file__))
    return os.path.abspath(os.path.join(dir_name,*paths))

def get_request(url,abs_filename=None,github_404=None,proxy=None,timeout=5,retry=3):
    """
    爬取github网页存放到本地
    :param url:
    :param abs_filename:
    :param proxy:
    :param timeout:
    :return:
    """
    ret=False
    s=requests.session()
    r=s.get(url,proxies=proxy,timeout=timeout)

    while retry>0:
        try:
            if r.status_code==200:
                if abs_filename:
                    content=r.content
                    with codecs.open(abs_filename,'wb') as f:
                        f.write(content)
                    ret=True
                else:
                    ret=r
                retry=0
            elif r.status_code==404:
                if github_404:
                    with codecs.open(github_404,'ab') as f:
                        f.write(url.encode()+b'\r\n')
                retry=0
            else:
                logging.info("%d [url] %s %s" (retry,url,r.status_code))
                retry=retry-1

        except Exception as e:
            print(str(e))
            retry=retry-1
    return ret

def strip_n(st):
    """

    :param st:
    :return:
    """
    if not st:
        return st

    st = re.sub(r'\n', ' ', st)
    st = re.sub(r'\s+', ' ', st)
    st = re.sub(r'\x22', '', st)
    st = re.sub(r'\x27', '', st)

    st = st.strip()
    return st

def get_github_info(url,github_dir='data/github'):
    """
    获取github账号的相关信息，依次类推可爬取微信公众号、网页、Twitter
    : param url:
    : param github_dir:
    : return:
    """
    # 判断url状态是否是404
    github_404=path('data/github_404')
    url_404=set()
    if os.path.exists(github_404):
        with codecs.open(github_404,'rb') as f:
            for line in f:
                line=line.strip()
                url_404.add(line)
    match=re.search("(https://github.com/([^/]+))",url)
    if match:
        github_url,github_id=match.groups()
        if github_url in url_404:
            return
    else:
        return

    # 创建存放github网页的离线目录和文件
    github_dir=path(github_dir)
    if not os.path.exists(github_dir):
        os.mkdir(github_dir)

    md5=hashlib.md5()
    md5.update(url.encode('utf-8'))
    filename=md5.hexdigest()
    abs_filename=path(github_dir,filename)
    if not os.path.exists(abs_filename):
        get_request(github_url,abs_filename,github_404) # 爬取网页并存放到本地

    if os.path.exists(abs_filename):
        with codecs.open(abs_filename,'rb') as f:
            try:
                soup=BeautifulSoup(f,features="lxml")
            except Exception as e:
                logging.info('GET %s failed:%s' %(url,repr(e)))

            # starting parse 
            overview={}

            # repo/projects/star/following/
            for i in soup.find_all("a",class_=re.compile('UnderlineNav-item')):
                ii=i.get_text()
                ii=strip_n(ii)
                if ii:
                    parts=re.split(r'\s+',ii)
                    if len(parts)==2:
                        overview["p_%s" %parts[0].lower()]=parts[1]

            # people cv
            p_profile=soup.find("div",class_=re.compile('p-note user-profile-bio'))
            if p_profile:
                p_profile=strip_n(p_profile.get_text())
            overview['p_profile']=p_profile

            # company
            p_company=soup.find('span',class_=re.compile('p-org'))
            if p_company:
                p_company=strip_n(p_company.get_text())
            overview['p_company']=p_company

            # geo
            p_geo=soup.find("span",class_=re.compile('p-label'))
            if p_geo:
                p_geo=strip_n(p_geo.get_text())
            overview['p_geo']=p_geo

            # blog
            p_blog=soup.find("div",class_=re.compile('js-profile-editable-area'))
            if p_blog:
                a_url=p_blog.find_all('a')
                for a in a_url:
                    a_text=a.get_text()
                    if a_text.startswith('http'):
                        p_blog=a_text
                    else:
                        p_url=""
            overview['p_blog']=p_blog

            # organizations
            p_org_list=[]
            for p_org in soup.find_all("a",class_=re.compile('avatar-group-item')):
                p_org=p_org.get("aria-label")
                p_org_list.append(p_org)
            p_org_list=list(set(p_org_list))
            p_org_list=','.join(p_org_list)
            if not p_org_list:
                p_org_list=None
            overview['p_org_list']=p_org_list

            # code language
            p_lan_list=[]
            for p_lan in soup.find_all(itemprop="programmingLanguage"):
                p_lan=p_lan.get_text()
                p_lan_list.append(p_lan)
            p_lan_list=list(set(p_lan_list))
            p_lan_list=','.join(p_lan_list)
            if not p_lan_list:
                p_lan_list=None
            overview['p_lan_list']=p_lan_list

    return overview

def date_delta(delta=0,format="%Y%m%d"):
    """
    按照当天时间前进或回退delta时间
    :param delta:
    :param format:
    :return:
    """
    date=(datetime.date.today()+datetime.timedelta(days=delta)).strftime(format)
    return date

if __name__=='__main__':
    get_github_info('https://github.com/feeicn')
    date_delta(delta=-1)