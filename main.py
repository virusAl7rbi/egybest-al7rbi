from bs4 import BeautifulSoup
import requests
import re


class egybest:
    def __init__(self, query: str = '') -> None:
        self.result = []
        self.query = query.replace(' ', '%20')
        self.baseurl = 'https://nero.egybest.site'

    def get_all_episode(self, url) -> list:
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        e_urls = []
        for e in soup.find_all('a', {'class': 'movie'}):
            soup = BeautifulSoup(requests.get(e['href']).text, 'lxml')
            if soup.find('iframe', {'class': 'auto-size'}):
                iframe = soup.find('iframe', {'class': 'auto-size'})['src']
                time_for_e = soup.find_all('td')[12].text
                e_num = re.search('-ep-(.*)/', e['href']).group(1)
                rate = soup.find('span', {'itemprop': 'ratingValue'}).text
                data = self.base_url+iframe
                e_urls.append({
                    "number": e_num,
                    "url": str(data),
                    "time": str(time_for_e),
                    "rate": str(rate)
                })
        return e_urls

    def main(self) -> list:
        search_query = self.query
        search_url = f"https://nero.egybest.site/explore/?q={search_query}"
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
                    "title": url.split("/")[4].replace('-', ' '),
                    "image": "https:" + soup.find('img')['src'],
                    "type": url.split("/")[3],
                    "rate": soup.find('span', {'itemprop': 'ratingValue'}).text,
                    "time": soup.find_all('td')[10].text,
                    "url": self.base_url + soup.find('iframe', {'class': 'auto-size'})['src']
                }
                self.result.append(data)
                
                
            elif url.split("/")[3] == "series":
                soup = BeautifulSoup(requests.get(url).text, 'lxml')
                sessons = soup.find_all('div', {'class': 'contents movies_small'})
                for i in sessons:
                    urls = i.find_all('a', {'class': 'movie'})
                    for x in urls:
                        if re.search('/season/', str(x)):
                            s_num = x['href'].split(
                                '/')[4].split('-season-')[1].split('-')[0]
                            self.result.append({
                                "season": str(s_num),
                                "type": url.split("/")[3],
                                "episodes": self.get_all_episode(x['href']),
                                "title": x.find('img')['alt'].replace('-', ' '),
                                "url": x['href'],
                                "image": "https:" + x.find('img')['src']
                            })
        return
