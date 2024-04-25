from src import *

if __name__ == '__main__':
    sup = initSupabase()
    data = Data


    #parseParas('08.04', date=datetime(2024, 4, 8), sup=sup, data=data)
    # link = "https://www.uksivt.ru/storage/files/all/ZAMENY/%D0%B0%D0%BF%D1%80%D0%B5%D0%BB%D1%8C/06.04.24%D0%B3..pdf"
    #link, date = getLastZamenaLink(soup=soup)
    # print(link)
    # hash_value = get_remote_file_hash(link)
    # print(hash_value)
    # filename=f"zam-{date}"
    # downloadFile(link=link, filename=filename+".pdf")
    # cv = Converter(f'{filename}.pdf')
    # cv.convert(f'{filename}.docx', start=0, end=None)
    # cv.close()
    # parseZamenas(f"zam-{date}.docx", date, sup=sup, data=data)
    # addNewZamenaFileLink(link,date=date,sup=sup)

    #zamenas = get_zamena_file_links()
    #print(zamenas[0].link)
    pass

#docker build -t eventgamer67/my-schedule .чч

