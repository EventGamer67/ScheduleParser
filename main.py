import supabase
from aiogram.fsm.storage import redis
from bs4 import BeautifulSoup

from dataModel import Data
from downloader import *
from pdf2docx import Converter, Page
from pdf2docx import *
from supbase import *
import datetime

if __name__ == '__main__':
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    sup = initSupabase()
    data = Data
    data.GROUPS = getGroups(sup=sup)
    data.CABINETS = getCabinets(sup=sup)
    data.TEACHERS = getTeachers(sup=sup)
    data.COURSES = getCourses(sup=sup)

    #print(getMonthTable(soup=soup,monthIndex=0))
    #print(getMonthsList(soup))
    #print(getMonthAvalibleDays(soup=soup,monthIndex=0))
    # print(getLastZamenaLink(soup=soup))
    #parserv2(soup=soup)

    # file = getLatestSchedleFile()
    # print(f'latest month {getLatestScheduleMonth()}')
    # print(f'latest month day link {getLatestSchedleFile()}')

    # print(getDaylink(soup=soup,monthIndex=0,day=23))
    # downloadFile(link=link,filename='last.docx')
    # print(getFileHash('last.docx'))
    # print(getParsedsHashes())

    # #print(getMonthAvalibleDays(soup=soup, monthIndex=0))
    # downloadFile(link=link, filename=f"date.pdf")

    # link = getLastZamenaLink(soup=soup)
    # date = getLastZamenaDate(soup=soup)
    # filename="zam-23"
    # downloadFile(link=link, filename=filename+".pdf")
    # cv = Converter(f'{filename}.pdf')
    # cv.convert(f'{filename}.docx', start=0, end=None)
    # cv.close()
    # date = datetime.date(2024, 1, 23)
    # parseZamenas(f'{filename}.docx',date=date,sup=initSupabase())
    # addNewZamenaFileLink(link,date=date)

    # siteLinks = getAllTablesLinks(getAllMonthTables(soup=soup))
    # for i in siteLinks:
    #     addNewZamenaFileLink(i,sup=sup,date=datetime.date(2024,2,5))

    #parseParas('29', date=datetime.date(2024,2,26), sup=sup, data=data)
    #parseParas('29', date=datetime.date(2024, 3, 4), sup=sup, data=data)
    #parseParas('rasp29', date=datetime.date(2024, 2, 12), sup=sup, data=data)
    #parseParas('29', date=datetime.date(2024, 3, 11), sup=sup, data=data)

    link = getLastZamenaLink(soup=soup)
    print(link)
    filename="zam-14"
    # downloadFile(link=link, filename=filename+".pdf")
    # cv = Converter(f'{filename}.pdf')
    # cv.convert(f'{filename}.docx', start=0, end=None)
    # cv.close()
    date = datetime.date(2024, 3, 14)
    parseZamenas("zam-14.docx", date, sup=sup, data=data)
    addNewZamenaFileLink(link,date=date,sup=sup)
    pass




# def extract_tables_from_docx(docx_path):
#     doc = docx.Document(docx_path)
#     tables = doc.tables
#     for table in tables:
#         for row in table.rows:
#             rows.append(row.cells)
#             # for cell in row.cells:
#             #     print(cell.text)
#
# url = "https://www.uksivt.ru/zameny"
# BASEURL = "https://www.uksivt.ru/"
#
# html = urlopen(url).read()
# soup = BeautifulSoup(html, 'html.parser')
#
# table = soup.find('table', {'class': 'ui-datepicker-calendar'})
# paragraphs_with_class = soup.find_all("p", class_="MsoNormal")
#
# for par in paragraphs_with_class:
#     if (par.get_text(strip=True) != '' and par.get_text(strip=True) is not None):
#         print(par.get_text(strip=True).split()[0])
#         break
#
# date = ''
# urls = []
# rows = table.find_all('tr')
# for row in rows:
#     cells = row.find_all('td')
#     for cell in cells:
#         link = cell.find('a')
#         if link:
#             href = link.get('href')
#             date = cell.get_text(strip=True)
#             if date.isdigit():
#                 print(f"Date: {date}, Href: {href}")
#                 file_url = urllib.parse.urljoin(BASEURL, href)
#                 urls.append(file_url)
#
#
# month = "Декабрь"  # Replace with your month variable
# encoded_month = urllib.parse.quote(month, safe='')
# encoded_date = urllib.parse.quote(date, safe='')
# filename = f"{month}_{date}.docx"
# response = requests.get(urls[-1])
# if response.status_code == 200:
#     with open(filename, 'wb') as file:
#         file.write(response.content)
#     print(f"File '{filename}' has been downloaded successfully.")
# else:
#     print("Failed to download the file.")


# Replace with your downloaded .docx file path
# docx_file = filename
# docx_file = "Декабрь_6.docx"
# rows = []
#
# def check_same_values(lst):
#     # Проверяем, все ли элементы списка равны первому элементу списка
#     return all(item == lst[0] for item in lst)
#
# def check_empty_list(lst):
#     # Проверяем каждый элемент списка на пустую строку
#     for item in lst:
#         if item != '':
#             return False  # Если хотя бы один элемент не пустой, возвращаем False
#     return True  # Если все элементы пустые строки, возвращаем True
#
# def check_same_value(cells):
#     # Get the first cell value to compare against others
#     first_value = cells[0]
#     sum = ''
#
#     # Compare all cells with the first cell value
#     for cell in cells[1:]:
#         sum = sum+cell
#         if cell != first_value:
#             return False
#
#     if(sum.strip() == ""):
#         return "Space"
#
#     # All cells contain the same value
#     return True
#
#
#
# # Replace with your downloaded .docx file path
# extract_tables_from_docx(docx_file)
#
# filtrerdRows = []
# zameny = [[]]
#
# rowC = 0
# for row in rows:
#     filtrerdRows.append([rows[rowC][0].text ,rows[rowC][1].text,rows[rowC][2].text, rows[rowC][3].text ,rows[rowC][4].text ,rows[rowC][5].text ,rows[rowC][6].text])
#     rowC += 1
#
# zamenyCounter = 0
#
# for row in filtrerdRows:
#
#     if(check_empty_list(row)):
#         zamenyCounter += 1
#         zameny.append([])
#         continue
#     # if (check_same_value(row) == "Space"):
#     #     print("Пробел")
#     #     zamenyCounter += 1
#     #     zameny.append([])
#     #     continue
#     zameny[zamenyCounter].append(row)
#     #zameny[zamenyCounter].append(row)
#
#     # if(check_same_value(row)):
#     #     tempbuffer = []
#     #     print("Замена целиков")
#     #     continue
#
#     #print(row)
#
# def defineZamenaType(zamenaGroup):
#     if(check_same_values(zamenaGroup[0])):
#         return "Full"
#     else:
#         return "Once"
#
# if(defineZamenaType(zameny[2]) == "Full"):
#     zamenaGruop = zameny[1][0][0].strip()
#     print(f"Заменяемая группа {zamenaGruop}")
#     for zam in range(1, len(zameny[1])):
#         lesson = zameny[1][zam][4]
#         teacher = zameny[1][zam][5]
#         cab = zameny[1][zam][6]
#         number = zameny[1][zam][1]
#         print(f"Заменяемый предмет {lesson}\n"
#               f"Предметник {teacher}\n"
#               f"Кабинет {cab}\n"
#               f"Пара {number}")
# else:
#     print(f"Заменяемая группа {zameny[2][0][0].strip()}")
#     for zam in range(0, len(zameny[2])):
#         lesson = zameny[2][zam][4]
#         teacher = zameny[2][zam][5]
#         cab = zameny[2][zam][6]
#         number = zameny[2][zam][1]
#         print(f"Заменяемый предмет {lesson}\n"
#               f"Предметник {teacher}\n"
#               f"Кабинет {cab}\n"
#               f"Пара {number}")
