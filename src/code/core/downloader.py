import asyncio
import os
import urllib
import fitz
import requests
from bs4 import BeautifulSoup
import re
from pdf2docx import Converter
import datetime
from urllib.request import urlopen
from src.code.tools.functions import get_remote_file_hash
from src.code.models.cabinet_model import Cabinet
from src.code.models.course_model import Course
from src.code.models.group_model import Group
from src.code.models.teacher_model import Teacher
from src.code.models.zamena_table_model import ZamTable
from src.code.network import supbase

SCHEDULE_URL = 'https://www.uksivt.ru/zameny'
# SCHEDULE_URL = 'http://127.0.0.1:3000/c:/Users/Danil/Desktop/Uksivt/sample.html'

BASEURL = 'https://www.uksivt.ru/'
from typing import List
from docx import Document
from docx.document import Document as DocumentType
from docx.table import Table


async def save_pixmap(pixmap, screenshot_path):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, pixmap.save, screenshot_path, "png")


def cleanup_temp_files(file_paths):
    for file_path in file_paths:
        os.remove(file_path)


async def create_pdf_screenshots(pdf_path):
    screenshot_paths = []
    pdf_document: fitz.Document = fitz.open(f"{pdf_path}.pdf")
    for i in range(pdf_document.page_count):
        page: fitz.Page = pdf_document.load_page(i)
        zoom_x = 1.5  # horizontal zoom
        zoom_y = 1.5  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix: fitz.Pixmap = page.get_pixmap(matrix=mat)
        screenshot_path = f'{pdf_path}_page_{i + 1}.png'
        await save_pixmap(pix, screenshot_path)
        screenshot_paths.append(screenshot_path)
    return screenshot_paths


def parseParas(filename: str, date, sup, data):
    cv = Converter(f'{filename}.pdf')
    cv.convert('schedule' + '.docx', start=0, end=None)
    cv.close()
    doc: DocumentType = Document('schedule.docx')
    groups = []
    for i in doc.paragraphs:
        text = i.text
        if (text.__contains__("Группа - ")):
            filter = text.split(' ')
            gr = supbase.get_groups_from_string(filter[-1], data=data)[0].name
            groups.append(gr)

    for i in groups:
        if get_group_by_id(target_name=i, sup=sup, groups=data.GROUPS, data=data):
            pass

    tables = []
    for i in doc.tables:
        tables.append(i)

    tables = extract_all_tables_to_rows(tables)
    fin = []
    temp = []
    for row in tables:
        try:
            if (len(row[0]) > 1):
                for w in row:
                    temp.append(w)
            else:
                temp.append(row)
        except:
            pass
        fin.append(i)

    temp = clearDiscipline(temp)
    temp = clearSingleStrings(temp)
    divided = defineGroups(groups, temp)
    for gruppa in divided:
        paras = divided[gruppa]
        divided[gruppa] = removeDuplicates(paras)
        paras = divided[gruppa]
        divided[gruppa] = removeDoubleRows(paras)
        paras = divided[gruppa]
        divided[gruppa] = recoverTeachers(paras)
        print(gruppa)
        ParasGroupToSoup(group=get_group_by_id(target_name=gruppa, groups=data.GROUPS, sup=sup, data=data),
                         paras=divided[gruppa], sup=sup, startday=date, data=data)
    pass


def parseZamenas(filename: str, date, sup, data, link:str):
    all_rows, header = get_all_tables(filename)

    practice_groups: List[Group] = []
    for i in header:
        practice_groups.extend(supbase.get_groups_from_string(i.text, data=data))

    workRows = []
    for i in all_rows:
        if (not is_nested(i)):
            workRows.extend(i)
        else:
            workRows.append(i)

    # test cleaning before ликвидация замен
    temp = []

    for i in workRows:
        if len(i) == 7:
            temp.append(i)

    workRows = temp

    for i in workRows:
        if i[2] == '' and i[3] != '':
            i[3] = ''
        if i[1] == '' and i[2] == '' and i[3] == '' and i[5] == '':
            i[4] = ''
            pass

    workRows = clearNonDataRows(workRows)
    workRows = clear_empty_sublists(workRows)
    workRows = remove_headers(workRows)

    fullzamenagroups = []
    liquidation = []
    iteration = 0

    for i in workRows:
        iteration = iteration + 1
        if i[0] == '':
            i[0] = workRows[iteration - 2][0]

    for i in workRows[:]:
        if i[0] == i[1] and i[2] == i[3]:
            if (i[0].strip().lower().__contains__("ликвидация")):
                try:
                    sample = i[0].strip().lower()
                    for gr in data.GROUPS:
                        if (sample.__contains__(gr.name.lower().strip())):
                            liquidation.append(gr.id)
                            print(f"Ликвидация {gr.name}")
                except Exception as err:
                    print(err)
                    continue
                workRows.remove(i)

    for i in workRows[:]:
        i.pop(2)

    for i in workRows[:]:
        i.pop(2)

    for i in workRows[:]:
        if (i[1] == '' and i[2] == '' and i[3] == '' and i[4] == ''):
            workRows.remove(i)

    for i in workRows[:]:
        if i[0] == i[1] and i[1] == i[2] and i[2] == i[3] and i[3] == i[4]:
            fullzamenagroups.append(i[0].strip().replace(' ', ""))
            workRows.remove(i)

    #чистка столбца группы
    #удаляет лишние -, пробелы, запятые, точки и приводит к uppercase
    cleaned_groups_workrows = []
    for i in workRows:
        i[0] = i[0].replace(' ','').replace(',','').replace('.','').upper()
        i[0] = re.sub(r'-{2,}', '-', i[0])

    editet = []
    for i in workRows:
        try:
            text = i[1].replace('.',',')
            if text[-1] == ',':
                text = text[0:-1]
                i[1] = text
            if text[0] == ',':
                text = text[0:len(text) - 1]
                i[1] = text
            paras = i[1].split(',')
            row = i.copy()
            if (len(paras) >= 2):
                for para in paras:
                    new = row.copy()
                    new[1] = para
                    editet.append(new)
            else:
                editet.append(i)
        except Exception as error:
            print(error)
            print(i)
            continue
    workRows = editet

    for row in workRows:
        group = get_group_by_id(data.GROUPS, row[0], sup=sup, data=data)
        if group is not None:
            row[0] = group.id

    for row in workRows:
        print(row[2])
        course = get_course_by_id(data.COURSES, row[2], sup=sup, data=data)
        if course is not None:
            row[2] = course.id

    for row in workRows:
        print(row[3])
        teacher = get_teacher_by_id(data.TEACHERS, row[3], sup=sup, data=data)
        if teacher is not None:
            row[3] = teacher.id

    for row in workRows:
        cabinet = get_cabinet_by_id(data.CABINETS, row[4], sup=sup, data=data)
        if cabinet is not None:
            row[4] = cabinet.id

    practice_supabase = []
    for i in practice_groups:
        practice_supabase.append({"group": i.id, 'date': str(date)})
        pass

    zamenas_supabase = []
    for i in workRows:
        zamenas_supabase.append(
            {"group": i[0], 'number': int(i[1]), 'course': i[2], 'teacher': i[3], 'cabinet': i[4], 'date': str(date)})
        pass

    full_zamenas_groups = []
    for i in fullzamenagroups:
        full_zamenas_groups.append(
            {"group": get_group_by_id(target_name=i, data=data, groups=data.GROUPS, sup=sup).id, 'date': str(date)})
        pass

    liquidations = []
    for i in liquidation:
        liquidations.append({"group": i, 'date': str(date)})
        pass

    supbase.addZamenas(sup=sup, zamenas=zamenas_supabase)
    if len(full_zamenas_groups) > 0:
        supbase.addFullZamenaGroups(sup=sup, groups=full_zamenas_groups)
    if len(practice_supabase) > 0:
        supbase.add_practices(sup=sup, practices=practice_supabase)
    if len(liquidations) > 0:
        supbase.addLiquidations(sup=sup, liquidations=liquidations)
    hash = get_remote_file_hash(link)
    supbase.addNewZamenaFileLink(link,date=date,sup=sup, hash=hash)
    pass



def removeDoubleRows(table):
    alreadyExist = []
    for row in table:
        if (not row in alreadyExist):
            alreadyExist.append(row)
    return alreadyExist


def removeDuplicates(table):
    index = 0
    cleared = []
    for row in table:
        if ((table[index - 1])[0] == row[0]):
            continue
        else:
            cleared.append(row)
            index = index + 1
    return cleared


def ParasGroupToSoup(group, paras, startday, sup, data):
    date = startday
    supabasePARA = []
    for para in paras:
        number = para[0]
        ParaMonday: str = para[1]
        paraTuesday: str = para[3]
        paraWednesday: str = para[5]
        paraThursday: str = para[7]
        paraFriday: str = para[9]
        paraSaturday: str = para[11]
        days = [ParaMonday, paraTuesday, paraWednesday, paraThursday, paraFriday, paraSaturday]

        loopindex = 0
        for day in days:
            aww = supbase.getParaNameAndTeacher(day)
            if aww is not None:
                teacher = get_teacher_by_id(target_name=aww[0], teachers=data.TEACHERS, sup=sup, data=data)
                course = get_course_by_id(target_name=aww[1], courses=data.COURSES, sup=sup, data=data)
                cabinet = get_cabinet_by_id(target_name=para[2 * (loopindex + 1)], cabinets=data.CABINETS, sup=sup,
                                            data=data)
                if (teacher is not None and course is not None and cabinet is not None):
                    supabasePARA.append(
                        {'group': group.id, 'number': number, 'course': course.id, 'teacher': teacher.id,
                         'cabinet': cabinet.id, 'date': str(date + datetime.timedelta(days=loopindex))})
                    pass
            loopindex = loopindex + 1
            pass
    sup.table('Paras').insert(supabasePARA).execute()
    pass


def recoverTeachers(table):
    aww = 0
    for row in table:
        if (row[0] == ''):
            if (len(row[1].split(' ')) > 2):
                text = table[aww - 1][1]
                table[aww - 1][1] = text + " \n" + row[1]
            if (len(row[3].split(' ')) > 2):
                text = table[aww - 1][3]
                table[aww - 1][3] = text + " \n" + row[3]
            if (len(row[5].split(' ')) > 2):
                text = table[aww - 1][5]
                table[aww - 1][5] = text + " \n" + row[5]
            if (len(row[7].split(' ')) > 2):
                text = table[aww - 1][7]
                table[aww - 1][7] = text + " \n" + row[7]
            if (len(row[9].split(' ')) > 2):
                text = table[aww - 1][9]
                table[aww - 1][9] = text + " \n" + row[9]
            if (len(row[11].split(' ')) > 2):
                text = table[aww - 1][11]
                table[aww - 1][11] = text + " \n" + row[11]
            table.remove(row)
        aww += 1
    return table


def defineGroups(groups, table):
    groupIndex = -1
    groupParas = []
    group = 'x'
    divided = {}
    for row in table:
        if (row[0] == '№'):
            divided[group] = groupParas
            groupIndex = groupIndex + 1
            group = groups[groupIndex]
            groupParas = []
        else:
            groupParas.append(row)
        pass
    else:
        divided[group] = groupParas
        pass
    divided.pop('x')
    return divided


def clearSingleStrings(table):
    cleared = []
    for row in table:
        if (not isinstance(row, str)):
            cleared.append(row)
    return cleared


def clearDiscipline(table):
    for row in table:
        if (len(row) >= 12):
            if (row[0] == '' and row[1] == '' and row[2] == '' and row[3] == '' and row[4] == '' and row[5] == '' and
                    row[6] == ''):
                table.remove(row)
                continue
            if (row[1].__contains__("Дисциплина, вид занятия, преподаватель")):
                table.remove(row)
                continue
            pass
    return table


def get_cabinet_by_id(cabinets, target_name, sup, data) -> Cabinet:
    for cabinet in cabinets:
        if cabinet.name == target_name:
            return cabinet
        else:
            continue
    try:
        supbase.addCabinet(target_name, sup=sup, data=data)
        return get_cabinet_by_id(cabinets=data.CABINETS, target_name=target_name, sup=sup, data=data)
    except:
        return None
    return None


def count_different_characters(str1, str2):
    if len(str1) != len(str2):
        return -1

    count = 0
    for char1, char2 in zip(str1, str2):
        if char1 != char2:
            count += 1
    return count


def get_teacher_from_short_name(teachers: List[Teacher], shortName: str):
    for i in teachers:
        fio: List[str] = i.name.split(' ')
        if len(fio) > 2 and fio[0].strip() != '' and fio[1].strip() != '' and fio[2].strip() != '':
            compare_result = f"{fio[0]}{fio[1][0]}{fio[2][0]}".lower().strip()
            shortcomparer = shortName.replace('.', '').replace(',', '').replace(' ', '').lower().strip()
            if compare_result == shortcomparer:
                return i
            else:
                if count_different_characters(compare_result, shortcomparer) == 1:
                    print(f"taker {compare_result} and {shortcomparer}")
                    print(f"set {i}")
                    return i
    return None


def get_teacher_by_id(teachers, target_name, sup, data) -> Teacher:
    for teacher in teachers:
        if teacher.name == target_name:
            return teacher
        else:
            search = get_teacher_from_short_name(teachers=teachers, shortName=target_name)
            if search is not None:
                return search
    try:
        supbase.addTeacher(target_name, sup=sup, data=data)
        print(f"want add teacher {target_name}")
        return get_teacher_by_id(teachers=data.TEACHERS, target_name=target_name, sup=sup, data=data)
    except:
        return None


def get_group_by_id(groups, target_name, sup, data) -> Group:
    for group in groups:
        if group.name.upper() == target_name.replace('_','-').upper():
            return group
        else:
            continue
    try:
        print(target_name)
        supbase.addGroup(target_name.upper(), sup=sup, data=data)
        return get_group_by_id(groups=data.GROUPS, target_name=target_name.upper(), sup=sup, data=data)
    except:
        return None
    return None


def get_course_by_id(courses, target_name, sup, data) -> Course:
    for course in courses:
        if course.name == target_name:
            return course
        else:
            continue
    try:
        supbase.addCourse(target_name, sup=sup, data=data)
        return get_course_by_id(data.COURSES, target_name=target_name, sup=sup, data=data)
    except:
        return None
    return None


def extract_all_tables_to_rows(tables: List[Table]) -> List[List[str]]:
    rows = []
    for table in tables:
        for row in table.rows:
            data = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                if cell.tables:
                    nested_table_rows = extract_all_tables_to_rows(cell.tables)
                    data.extend(nested_table_rows)
                else:
                    data.append(cell_text)
            rows.append(data)
    return rows


def is_nested(row: List[str]) -> bool:
    return isinstance(row, List) and all(isinstance(item, str) for item in row)


def remove_duplicates(input_list):
    unique_list = []
    for sublist in input_list:
        if sublist not in unique_list:
            unique_list.append(sublist)
    return unique_list


def check_family(i):
    if (len(i[1].split(' ')) > 2) or (len(i[3].split(' ')) > 2) or (len(i[5].split(' ')) > 2) or (
            len(i[7].split(' ')) > 2) or (len(i[9].split(' ')) > 2) or (len(i[11].split(' ')) > 2):
        if (i[2] == '' and i[4] == '' and i[6] == '' and i[8] == '' and i[10] == '' and i[12] == ''):
            return True
    return False


def remove_headers(rows):
    cleared = []
    for i in rows:
        if (i[0] != "Группа"):
            cleared.append(i)
    return cleared


def get_all_tables(filename: str):
    doc: DocumentType = Document(filename)
    tables = doc.tables
    all_rows = extract_all_tables_to_rows(tables)
    return all_rows, doc.paragraphs


def clear_empty_sublists(nested_list: List[List[str]]) -> List[List[str]]:
    return [sublist for sublist in nested_list if any(item != '' for item in sublist)]


def clearNonDataRows(rows: List[List[str]]) -> List[List[str]]:
    filtered_rows = [row for row in rows if len(row) >= 7]
    return filtered_rows


def downloadFile(link: str, filename: str):
    response = requests.get(link)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"File '{filename}' has been downloaded successfully.")
    else:
        print("Failed to download the file.")


def getLastZamenaLink(soup: BeautifulSoup):
    # days, month = getMonthAvalibleDays(soup=soup, monthIndex=0)
    # day = days[-1]
    # year = datetime.datetime.now().year.real
    # date = datetime.date(year=year, month=month, day=day)
    table = getAllMonthTables(soup)[0]
    return table.zamenas[-1].link, table.zamenas[-1].date


def getLastZamenaDate(soup: BeautifulSoup):
    days = getMonthAvalibleDays(soup=soup, monthIndex=0)
    month, year = str(getMonthsList(soup=soup)[0]).split(' ')
    date = datetime.date(2024, convertMonthNameToIndex(month) + 1, days[-1])
    return date


def getDaylink(soup: BeautifulSoup, monthIndex: int, day: int):
    table, month = getMonthTable(soup=soup, monthIndex=monthIndex)
    for link in table.find_all('a'):
        text = link.get_text()
        if (link):
            if (text.isdigit() and int(text) == day):
                return link.get('href')


def convertMonthNameToIndex(name: str):
    months = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь',
              'декабрь']
    return months.index(name.lower())


def getMonthTable(soup: BeautifulSoup, monthIndex: int):
    newtables = soup.find_all(name='table')
    #newtables = soup.find_all('table', {'class': 'MsoNormalTable'})
    #oldtables = soup.find_all('table', {'class': 'calendar-month'})
    #newtables.extend(oldtables)
    month = convertMonthNameToIndex(newtables[monthIndex].find_all('td',{'class':'calendar-month-title'})[0].get_text().split(' ')[0]) + 1
    tables = getAllMonthTables(soup)
    return newtables[monthIndex], month


def getAllMonthTables(soup: BeautifulSoup) -> List[ZamTable]:
    zam_tables: List[ZamTable] = []
    new_tables = soup.find_all(name='table')
    for i in new_tables:
        class_type = ''.join(i['class']).strip()
        if class_type == 'calendar-month':
            if len(i.find_all('td', {'class': 'calendar-month-title'})) == 0:
                header = "Ничего"
                if(i.find_all('a',{'class':'calendar-month-title'})):
                    header = i.find_next('a',{'class':'calendar-month-title'}).get_text()
                else:
                    header = i.find_previous().find_previous().get_text().replace('\xa0', '')
                year = int(datetime.datetime.now().year)
                if(len(header.split(' ')) > 1):
                    index = convertMonthNameToIndex(header.split(' ')[0])
                    year = int(header.split(' ')[1])
                else:
                    index = convertMonthNameToIndex(header.replace(' ',''))
                zam_tables.append(ZamTable(raw=i, month_index=index + 1,year=year))
                pass
            else:
                header = i.find_all('td', {'class': 'calendar-month-title'})[0].get_text().replace('\xa0', '').split(' ')
                index = convertMonthNameToIndex(header[0])
                year = int(header[1])
                zam_tables.append(ZamTable(raw=i, month_index=index + 1,year=year))
            pass
        if class_type == 'MsoNormalTable':
            header = i.find_next(name='strong').get_text().replace('\xa0', '')
            year = 2024
            index = convertMonthNameToIndex(header)
            zam_tables.append(ZamTable(raw=i, month_index=index + 1,year=year))
            pass
        if class_type == 'ui-datepicker-calendar':
            header = i.find_previous().get_text().replace('\xa0', '').split(' ')
            index = convertMonthNameToIndex(header[0])
            year = int(header[1])
            zam_tables.append(ZamTable(raw=i, month_index=index + 1,year=year))
            pass
    return zam_tables


def getAllTablesLinks(tables: List[ZamTable]) -> List[str]:
    links: List[str] = []
    for table in tables:
        links.extend(table.links)
    return links


def getMonthAvalibleDays(soup: BeautifulSoup, monthIndex: int):
    days = []
    table, month = getMonthTable(soup=soup, monthIndex=monthIndex)
    links = table.find_all('a')
    for link in links:
        if (link.get_text().isdigit()):
            if (link):
                days.append(int(link.get_text()))
    return days, month


def getMonthsList(soup: BeautifulSoup):
    paragraphs_with_class = soup.find_all("p", class_="MsoNormal")
    list = []
    for par in paragraphs_with_class:
        paragraphText = par.get_text(strip=True)
        if (paragraphText != '' and paragraphText is not None and not paragraphText.isdigit() and paragraphText not in [
            'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']):
            list.append(par.get_text(strip=True))
    index = 0
    for month in list:
        if len(month.split(' ')) == 1:
            list[index] = f"{month} {list[index + 1].split(' ')[1]}"
        index = index + 1
    return list


def getLatestScheduleMonth(soup: BeautifulSoup) -> str:
    table = soup.find('table', {'class': 'ui-datepicker-calendar'})
    paragraphs_with_class = soup.find_all("p", class_="MsoNormal")

    for par in paragraphs_with_class:
        if (par.get_text(strip=True) != '' and par.get_text(strip=True) is not None):
            return par.get_text(strip=True).split()[0]


def getLatestSchedleFile():
    html = urlopen(SCHEDULE_URL).read()
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', {'class': 'calendar-month'})
    paragraphs_with_class = soup.find_all("p", class_="MsoNormal")

    for par in paragraphs_with_class:
        if (par.get_text(strip=True) != '' and par.get_text(strip=True) is not None):
            print(par.get_text(strip=True).split()[0])
            break
    urls = []
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        for cell in cells:
            link = cell.find('a')
            if link:
                href = link.get('href')
                date = cell.get_text(strip=True)
                if date.isdigit():
                    print(f"Date: {date}, Href: {href}")
                    file_url = urllib.parse.urljoin(BASEURL, href)
                    urls.append(file_url)

    return urls[-1]