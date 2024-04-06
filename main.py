import datetime

from downloader import *
from supbase import *
import hashlib

def get_file_hash(url, algorithm="sha256"):
    # Получение содержимого файла по URL
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # Вычисление хеша файла по содержимому
        hasher = hashlib.new(algorithm)
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                hasher.update(chunk)
        return hasher.hexdigest()
    else:
        return None

if __name__ == '__main__':
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    sup = initSupabase()
    data = Data
    data.GROUPS = getGroups(sup=sup)
    data.CABINETS = getCabinets(sup=sup)
    data.TEACHERS = getTeachers(sup=sup)
    data.COURSES = getCourses(sup=sup)

    #parseParas('08.04', date=datetime(2024, 4, 8), sup=sup, data=data)
    link = "https://www.uksivt.ru/storage/files/all/ZAMENY/%D0%B0%D0%BF%D1%80%D0%B5%D0%BB%D1%8C/06.04.24%D0%B3..pdf"
    #link, date = getLastZamenaLink(soup=soup)
    print(link)
    hash_value = get_file_hash(link)
    print(hash_value)
    # filename=f"zam-{date}"
    # downloadFile(link=link, filename=filename+".pdf")
    # cv = Converter(f'{filename}.pdf')
    # cv.convert(f'{filename}.docx', start=0, end=None)
    # cv.close()
    # parseZamenas(f"zam-{date}.docx", date, sup=sup, data=data)
    # addNewZamenaFileLink(link,date=date,sup=sup)
    pass

#docker build -t eventgamer67/my-schedule .чч


