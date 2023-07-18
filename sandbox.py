from airflow import DAG
import requests as req
from urllib.parse import urlsplit
import urllib.robotparser as urp
import re
from bs4 import BeautifulSoup
from html2text import html2text as htt
import sys

def hello(item=None):
    return None


#Parse RSS
def can_scrape(url: str):
    #Get robot URL
    url_parts = urlsplit(url)
    base_url = url_parts.scheme + "://" + url_parts.netloc
    robot_url = base_url + '/robots.txt'
    rp = urp.RobotFileParser()
    rp.set_url(robot_url)
    rp.read()
    return rp.can_fetch("*", url)


if __name__ == "__main__":
    url = 'https://techinasia.com/feed'
    #Check robots file
    # print(check_robots('https://techinasia.com'))
    if(can_scrape(url)):
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        res = req.get('https://aws.amazon.com/blogs/machine-learning/feed/', headers=header)
        soup = BeautifulSoup(res.content, features='xml')
        articles = soup.findAll('item')
        
        article_list = []
        for a in articles:
            title = a.find('title').text
            link = a.find('link').text
            published = a.find('pubDate').text
            description = a.find('description').text

            article = {
                'title': title,
                'link': link,
                'published': published,
                'description': htt(description)
                }
            article_list.append(article)

        idx = 4
        print(htt(article_list[idx]['description']))
        print(article_list[idx]['title'])
        print(article_list[idx]['published'])
        print(sys.getsizeof(article_list))
        