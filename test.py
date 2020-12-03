from termcolor import colored, cprint
from pyshorteners import Shortener
from bs4 import BeautifulSoup
from time import time
from sys import argv
import requests
import re
import os

os.system('cls')

def get_all_episode(url):
    base_url = 'https://nero.egybest.site'
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    e_urls = []
    for e in soup.find_all('a', {'class': 'movie'}):
        soup = BeautifulSoup(requests.get(e['href']).text, 'lxml')
        if soup.find('iframe', {'class': 'auto-size'}):
            iframe = soup.find('iframe', {'class': 'auto-size'})['src']
            time_for_e = soup.find_all('td')[12].text
            e_num = e['href'].split('/')[4].split('-ep-')[1]
            rate = soup.find('span', {'itemprop': 'ratingValue'}).text
            data = f"{base_url}{iframe}"
            e_urls.append({
                "number": str(e_num),
                "url": Shortener().dagd.short(str(data)),
                "time": str(time_for_e),
                "rate": str(rate)
            })
    return e_urls

result = []


def main(q):
    print('Starting search...')
    search_query = str(q).replace(' ', '%20')
    search_url = f"https://nero.egybest.site/explore/?q={search_query}"
    base_url = 'https://nero.egybest.site'
    req = requests.get(search_url).text
    soup = BeautifulSoup(req, 'lxml')
    main_url = []
    for res in soup.find_all('a', {'class': 'movie'}):
        url = res['href'][:-15]
        main_url.append(url)
    for url in main_url:
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        if url.split("/")[3] == "movie" and soup.find('iframe', {'class': 'auto-size'}):
            soup = BeautifulSoup(requests.get(url).text, 'lxml')
            data = {
                "title": url.split("/")[4].replace('-',' '),
                "image": Shortener().dagd.short("https:" + soup.find('img')['src']),
                "type": url.split("/")[3],
                "rate": soup.find('span', {'itemprop': 'ratingValue'}).text,
                "time": soup.find_all('td')[10].text,
                "url": Shortener().dagd.short(base_url + soup.find('iframe', {'class': 'auto-size'})['src'])
            }
            result.append(data)
        elif url.split("/")[3] == "series":
            soup = BeautifulSoup(requests.get(url).text, 'lxml')
            sessons = soup.find_all('div', {'class': 'contents movies_small'})
            for i in sessons:
                urls = i.find_all('a', {'class': 'movie'})
                for x in urls:
                    if re.search('/season/', str(x)):
                        s_num = x['href'].split('/')[4].split('-season-')[1].split('-')[0]
                        result.append({
                            "season": str(s_num),
                            "type": url.split("/")[3],
                            "episodes": get_all_episode(x['href']),
                            "title": x.find('img')['alt'].replace('-',' '),
                            "url": Shortener().dagd.short(x['href']),
                            "image": Shortener().dagd.short("https:" + x.find('img')['src'])
                        })
    return

main(argv[1])

if len(result) > 1:
    for i in result:
        if i['type'] == 'movie':
            print("name : "+i['title'])
            print("image : "+i['image'])
            print("type : "+i['type'])
            print("rate : "+i['rate'])
            print("time : "+i['time'])
            print("url : "+i['url'])
            cprint('#############################','blue')
        if i['type'] == 'series':
            print("name : "+i['title'])
            print('season: '+i['season'])
            print("type : "+i['type'])
            print("image : "+i['image'])
            for x in i['episodes']:
                print('     number: '+x['number'])
                print('     url: '+x['url'])
                print('     time: '+x['time'])
                print('     rate: '+x['rate'])
                cprint('    #############################','red')
else:
    print('Nothing Found..')