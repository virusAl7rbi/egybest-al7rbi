from bs4 import BeautifulSoup, SoupStrainer
from time import time
from sys import argv
import requests
import re


def content(url, only: str = 'body', attrs: dict = {}):
    only = SoupStrainer(only, attrs)
    return BeautifulSoup(requests.get(url).text, 'lxml', parse_only=only)


def get_all_episode(url):
    base_url = 'https://nero.egybest.site'
    e_urls = []
    for e in content(url, only='a', attrs={'class': 'movie'}).find_all('a', {'class': 'movie'}):
        soup = content(url, only='body')
        if soup.find('iframe', {'class': 'auto-size'}):
            iframe = soup.find('iframe', {'class': 'auto-size'})['src']
            time_for_e = soup.find_all('td')[12].text
            e_num = result = re.search('-ep-(.*)/', e['href']).group(1)
            rate = soup.find('span', {'itemprop': 'ratingValue'}).text
            data = base_url + iframe
            e_urls.append({
                "number": str(e_num),
                "url": data,
                "time": str(time_for_e),
                "rate": str(rate)
            })
    return e_urls


result = []


def main(q):

    base_url = 'https://nero.egybest.site'
    soup = BeautifulSoup(requests.get(q).text, 'lxml')
    sessons = soup.find_all('div', {'class': 'contents movies_small'})
    for i in sessons:
        urls = i.find_all('a', {'class': 'movie'})
        for x in urls:
            if re.search('/season/', str(x)):
                print(re.search('-season-(.*)/', x['href']).group(1))
                s_num = re.search('-season-(.*)/', x['href']).group(1)
                result.append({
                    "season": str(s_num),
                    "episodes": get_all_episode(x['href']),
                    "title": x.find('img')['alt'].replace('-', ' '),
                    "url": x['href'],
                    "image": "https:" + x.find('img')['src']
                })


main("https://nero.egybest.site/season/lucifer-season-5/?ref=tv-p1")
