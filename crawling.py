import requests
from flask import request as rq

from bs4 import BeautifulSoup
import pandas as pd
import urllib.request
import json
import os


def get_public_dataset(keyword):
    resp = requests.get('https://www.data.go.kr/tcs/dss/selectDataSetList.do?dType=FILE&keyword={}&operator=AND&detailKeyword=&publicDataPk=&recmSe=&detailText=&relatedKeyword=&commaNotInData=&commaAndData=&commaOrData=&must_not=&tabId=&dataSetCoreTf=&coreDataNm=&sort=updtDt&relRadio=&orgFullName=&orgFilter=&org=&orgSearch=&currentPage=1&perPage=10&brm=&instt=&svcType=&kwrdArray=&extsn=&coreDataNmArray=&pblonsipScopeCode='.format(keyword))
    html = resp.text

    soup = BeautifulSoup(html, 'html.parser')

    titles = [i.text.strip().replace('_', ' ') for i in soup.select('.result-list .title')]
    links = [i.find('a')['href'] for i in soup.find(class_='result-list').find_all('dt')]

    result = []
    for i in range(len(titles)):
        result.append({
            "title": titles[i],
            "link": links[i],
        })
        if i==3: break
    return result

def get_news(keyword):
    API_KEY = os.environ.get("NAVER_KEY")
    SECRET_KEY = os.environ.get("NAVER_SECRET_KEY")

    client_id = API_KEY
    client_secret = SECRET_KEY
    encText = urllib.parse.quote(keyword)

    url = "https://openapi.naver.com/v1/search/news.json?query=" + encText # JSON 결과
    # url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText # XML 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if(rescode==200):
        result = json.load(response)

        titles = [i['title'] for i in result['items']]
        links = [i['link'] for i in result['items']]
        result = []
        for i in range(len(titles)):
            result.append({
                "title": titles[i],
                "link": links[i],
            })
            if i==3: break
        return result
    else:
        print("Error Code:" + rescode)  


def get_github_repos(keyword):
    resp = requests.get('https://github.com/search?q={}&type=repositories&p=1'.format(keyword))
    html = resp.text
    github_link = "https://github.com/"
    result = []
    try:
        res = json.loads(html)['payload']['results']
        titles = [i['hl_trunc_description'].replace('<em>', '').replace('</em>','') for i in res]
        links = [github_link + i['hl_name'] for i in res]
        for i in range(len(titles)):
            result.append({
                    "title": titles[i],
                    "link": links[i],
                })
        return result
    except:
        return result



