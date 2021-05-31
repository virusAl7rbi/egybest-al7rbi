from bs4 import BeautifulSoup
from time import time
from sys import argv
import requests
import re


def get_all_episode(url):
    base_url = 'https://nero.egybest.site'
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    e_urls = []
    for e in soup.find_all('a', {'class': 'movie'}):
        soup = BeautifulSoup(requests.get(e['href']).text, 'lxml')
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

print(get_all_episode("https://nero.egybest.site/season/lucifer-season-5/?ref=tv-p1")[0]['number'])