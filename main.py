import datetime

import bs4

from src import *

if __name__ == '__main__':
    #html = urlopen(SCHEDULE_URL).read()
    #soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    sup = initSupabase()
    data = Data(sup=sup)
    date = datetime.datetime(2024,5,6)
    link = "https://www.uksivt.ru//storage/files/all/ZAMENY/%D0%BC%D0%B0%D0%B9/06.05.24%D0%B3..pdf"
    #link, date = getLastZamenaLink(soup=soup)
    parse(link, date, sup)


    #parseParas('29.04', date=datetime.datetime(2024, 4, 29), sup=sup, data=data)
    pass


