import datetime

import bs4

from src import *
from src.code.models.data_model import DataMock, DataLoged
from src.firebase.firebase import send_message_to_topic

if __name__ == '__main__':
    # html = urlopen(SCHEDULE_URL).read()
    # soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')

    #data = Data(sup=sup)

    # date = datetime.datetime(2024,5,6)
    # link = "https://www.uksivt.ru//storage/files/all/ZAMENY/%D0%BC%D0%B0%D0%B9/06.05.24%D0%B3..pdf"
    # link, date = getLastZamenaLink(soup=soup)
    # parse(link, date, sup)

    #parseParas('10.06', date=datetime.datetime(2024, 6, 10), sup=sup, data=data)


    # sup = initSupabase()
    # send_message_to_topic( 'Новые замены', f'Новые замены на.',sup=sup)


    pass
