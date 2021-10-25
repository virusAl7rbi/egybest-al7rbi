from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from pyvirtualdisplay import Display
from bs4 import BeautifulSoup, SoupStrainer
import requests, re, time


class egybest:
    def __init__(self, query: str = "mr robot", res_type: str = "m") -> None:
        self.result_seasons, self.result_movies = [[]] * 2
        self.query = query.replace(" ", "%20")
        self.result_type = res_type {"m": "movie", "s": "series"}
        self.base_url = "https://lack.egybest.org"
        self.display = Display(
            visible=0, size=(1024, 768)
        )  # run before use ==> self.display.start()

    def webdriver(self):
        self.display.start()
        driver = Firefox(
            service=Service(GeckoDriverManager().install()),
        )
        return driver

    def content(self, url, only: str = "body", attrs: dict = {}):
        only = SoupStrainer(only, attrs)
        return BeautifulSoup(requests.get(url).text, "lxml", parse_only=only)

    def get_all_episode(self, url) -> list:
        soup = BeautifulSoup(requests.get(url).text, "lxml")
        e_urls = []
        for e in self.content(url, only="a", attrs={"class": "movie"}).find_all(
            "a", {"class": "movie"}
        ):
            soup = self.content(url)
            if soup.find("iframe", {"class": "auto-size"}):
                iframe = soup.find("iframe", {"class": "auto-size"})["src"]
                time_for_e = soup.find_all("td")[12].text
                e_num = re.search("-ep-(.*)/", e["href"]).group(1)
                rate = soup.find("span", {"itemprop": "ratingValue"}).text
                data = self.base_url + iframe
                e_urls.append(
                    {
                        "number": e_num,
                        "url": str(data),
                        "time": str(time_for_e),
                        "rate": str(rate),
                    }
                )
        return e_urls

    def main(self) -> list:
        search_query = self.query
        search_url = f"{self.base_url}/explore/?q={search_query}"
        soup = self.content(search_url)
        for res in soup.find_all("a", {"class": "movie"}):
            url = res["href"][:-15]
            soup = self.content(url)
            if url.split("/")[3] == "movie" and soup.find(
                "iframe", {"class": "auto-size"}
            ):
                soup = self.content(url)
                data = {
                    "title": url.split("/")[4].replace("-", " "),
                    "image": "https:" + soup.find("img")["src"],
                    "rate": soup.find("span", {"itemprop": "ratingValue"}).text,
                    "time": soup.find_all("td")[10].text,
                    "url": self.base_url
                    + soup.find("iframe", {"class": "auto-size"})["src"],
                }
                self.result_movies.append(data)

            elif url.split("/")[3] == "series":
                soup = self.content(url, "div", {"class": "contents movies_small"})
                for i in soup.find_all("div"):
                    urls = i.find_all("a", {"class": "movie"})
                    for x in urls:
                        if re.search("/season/", str(x)):
                            s_num = re.search("-season-(.*)/", x["href"]).group(1)
                            self.result_seasons.append(
                                {
                                    "season": str(s_num),
                                    "episodes": self.get_all_episode(x["href"]),
                                    "title": x.find("img")["alt"].replace("-", " "),
                                    "url": x["href"],
                                    "image": "https:" + x.find("img")["src"],
                                }
                            )

    def search_result(self):
        search_query = self.query
        search_url = f"{self.base_url}/explore/?q={search_query}"
        content = ""
        driver = self.webdriver()
        driver.get(search_url)
        page_hight = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == page_hight:
                content = driver.page_source
                driver.close()
                self.display.stop()
                break
            page_hight = new_height

        def type_check(a_tag):
            return re.findall("\/\w+\/", a_tag)[0].replace("/", "")

        def res_check(name):
            return any(x in name for x in search_query.replace("%20", " ").lower().split())

        soup = BeautifulSoup(
            content, "lxml", parse_only=SoupStrainer(id="movies")
        ).find_all("a")
        results = []

        for banner in soup:
            print(self.result_type)
            try:
                if res_check(banner.find(class_="title").text.lower()) and type_check(banner["href"]) == self.result_type:
                    data = {}
                    data["title"] = banner.find(class_="title").text
                    data["rate"] = float(banner.find(class_="rating").text) if banner.find(class_="rating") else 0
                    data["img"] = banner.find("img")["src"]
                    data["type"] = type_check(banner["href"])
                    data["url"] = banner["href"]
                    results.append(data)
            except Exception as e:
                print(banner)
                print(e)
                break
        from pprint import pprint

        pprint(results)
        print(len(results))


egybest().search_result()
