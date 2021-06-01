from bs4 import BeautifulSoup, SoupStrainer
import requests
import re


class egybest:
    def __init__(self, query: str = '') -> None:
        self.result_seasons, self.result_movies = [], []
        self.query = query.replace(' ', '%20')
        self.baseurl = 'https://nero.egybest.site'

    def content(self, url, only: str = 'body', attrs: dict = {}):
        only = SoupStrainer(only, attrs)
        return BeautifulSoup(requests.get(url).text, 'lxml', parse_only=only)

    def get_all_episode(self, url) -> list:
        soup = BeautifulSoup(requests.get(url).text, 'lxml')
        e_urls = []
        for e in self.content(url, only='a', attrs={'class': 'movie'}).find_all('a', {'class': 'movie'}):
            soup = self.content(url)
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
        soup = self.content(search_url)
        for res in soup.find_all('a', {'class': 'movie'}):
            url = res['href'][:-15]
            soup = self.content(url)
            if url.split("/")[3] == "movie" and soup.find('iframe', {'class': 'auto-size'}):
                soup = self.content(url)
                data = {
                    "title": url.split("/")[4].replace('-', ' '),
                    "image": "https:" + soup.find('img')['src'],
                    "rate": soup.find('span', {'itemprop': 'ratingValue'}).text,
                    "time": soup.find_all('td')[10].text,
                    "url": self.base_url + soup.find('iframe', {'class': 'auto-size'})['src']
                }
                self.result_movies.append(data)

            elif url.split("/")[3] == "series":
                soup = self.content(url,'div', {'class': 'contents movies_small'})
                for i in soup.find_all('div'):
                    urls = i.find_all('a', {'class': 'movie'})
                    for x in urls:
                        if re.search('/season/', str(x)):
                            s_num = re.search('-season-(.*)/', x['href']).group(1)
                            self.result_seasons.append({
                                "season": str(s_num),
                                "episodes": self.get_all_episode(x['href']),
                                "title": x.find('img')['alt'].replace('-', ' '),
                                "url": x['href'],
                                "image": "https:" + x.find('img')['src']
                            })
