import datetime
import urllib
from typing import List

from src.code.models.zamena_model import Zamena


class ZamTable:
    def __init__(self, raw, month_index: int, year: int):
        self.raw = raw
        self.month_index = month_index
        self.year = year
        self.zamenas: List[Zamena] = self.get_zamenas()
        self.links = self.get_links()


    def get_links(self):
        links = []
        for i in self.zamenas:
            links.append(i.link)
        return  links

    def get_zamenas(self):
        zamenas = []
        tags = self.raw.find_all('a')
        for tag in tags:
            text = tag.get_text()
            if (tag):
                if text.isdigit():
                    link = urllib.parse.urljoin("https://www.uksivt.ru/zameny/", tag.get('href'))
                    zamenas.append(Zamena(link=link, date=datetime.date(year=self.year,month=self.month_index, day=int(text))))
        return zamenas