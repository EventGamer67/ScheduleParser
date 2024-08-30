# import datetime
#
# import bs4
#
# from src import *
# from src.code.models.data_model import DataMock, DataLoged
# from src.firebase.firebase import send_message_to_topic
#
# if __name__ == '__main__':
#     html = urlopen(SCHEDULE_URL).read()
#     soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
#
#     sup = initSupabase()
#     data = Data(sup=sup)
#
#     date = datetime.datetime(2024,6,20)
#     link = "https://www.uksivt.ru//storage/files/all/ZAMENY/%D0%B8%D1%8E%D0%BD%D1%8C/20.06.24%D0%B3..docx.pdf"
#     #link, date = getLastZamenaLink(soup=soup)
#     parse(link, date, sup)
#     ##parseParas('10.06', date=datetime.datetime(2024, 6, 10), sup=sup, data=data)
#
#
#     # send_message_to_topic( 'Новые замены', f'Новые замены на.',sup=sup)
#
#
#     pass
#
#
# import datetime
#
# from bot_worker import parse
from src.code.core.downloader import parse_teacher_schedule

# parse(link="https://www.uksivt.ru/storage/files/all/ZAMENY/%D0%B0%D0%BF%D1%80%D0%B5%D0%BB%D1%8C/25.04.24%D0%B3..docx.pdf",date_=datetime.date(2024,8,30))

parse_teacher_schedule()