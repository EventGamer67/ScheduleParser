import datetime

import bs4

from src import *

if __name__ == '__main__':
    #html = urlopen(SCHEDULE_URL).read()
    #soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    sup = initSupabase()
    data = Data(sup=sup)
    #date = datetime.datetime(2024,1,31)
    #link = "https://www.uksivt.ru/storage/files/all/ZAMENY/%D0%AF%D0%BD%D0%B2%D0%B0%D1%80%D1%8C/31.01(2).pdf"
    #link, date = getLastZamenaLink(soup=soup)
    #parse(link, date, sup)


    parseParas('06.05', date=datetime.datetime(2024, 5, 6), sup=sup, data=data)
    pass


