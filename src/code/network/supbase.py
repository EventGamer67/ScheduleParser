import datetime
import logging
import os
import random
import re
from typing import List
import requests
import supabase
from pdf2docx import *
from supabase import create_client, Client
from parser_secrets import SUPABASE_URL, SUPABASE_ANON_KEY
from src.code.core.downloader import parseZamenas, get_teacher_from_short_name, get_teachers_from_string
from src.code.models.cabinet_model import Cabinet
from src.code.models.course_model import Course
from src.code.models.data_model import Data
from src.code.models.group_model import Group
from src.code.models.parsed_date_model import ParsedDate
from src.code.models.subscriber_model import Subscriber
from src.code.models.teacher_model import Teacher
from src.code.tools.logs import logger


def initSupabase():
    supabase: Client = create_client("https://ojbsikxdqcbuvamygezd.supabase.co",
                                     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9qYnNpa3hkcWNidXZhbXlnZXpkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcwOTQ1Mzg0NCwiZXhwIjoyMDI1MDI5ODQ0fQ.vDdfXpbYNoWgqP0c3I7M9G6oT0e_-UXnr_VCYNaHcOw")
    return supabase


def addGroup(name, sup, data):
    response = sup.table("Groups").insert({"name": name, "department": 0}).execute()
    data.GROUPS = getGroups(sup=sup)
    print(response)


def get_groups_from_string(string: str, data: Data,sup) -> List[Group]:
    groups = []
    for gr in data.GROUPS:
        if (string.lower().strip().__contains__(gr.name.lower().strip())):
            groups.append(gr)
    if len(groups) == 0:
        addGroup(string,sup,data)
    return groups


def getParsedsHashes():
    supa = initSupabase()
    response: supabase.APIResponse = supa.from_('parseddays').select('hash').execute()
    hashes = []
    for item in response.data:
        hashes.append(item['hash'])

    return hashes


def addPara(sup: Client, group, number, course, teacher, cabinet, date):
    sup.table('Paras').insert(
        {'group': group, 'number': number, 'course': course, 'teacher': teacher, 'cabinet': cabinet,
         'date': date}).execute()
    pass


def addNewZamenaFileLink(link: str, date, sup, hash : str):
    response = sup.table("ZamenaFileLinks").insert({"link": link, "date": str(date), "hash":hash}).execute()
    return response


def get_zamena_file_links() -> List[ParsedDate]:
    sup = initSupabase()
    response = sup.table("ZamenaFileLinks").select('*').execute()
    parsed_days: List[ParsedDate] = []
    for i in response.data:
        parsed_days.append(ParsedDate(date=i["date"],link=i["link"],filehash=i["hash"]))
    return parsed_days





def addCourse(name, sup, data):
    rnd = random.Random()
    color = f'{255},{rnd.randint(0, 255)},{rnd.randint(0, 255)},{rnd.randint(0, 255)}'
    response = sup.table("Courses").insert({"name": name, "color": color}).execute()
    data.COURSES = getCourses(sup=sup)
    print(response)


def addTeacher(name, sup, data):
    response = sup.table("Teachers").insert({"name": name}).execute()
    data.TEACHERS = getTeachers(sup=sup)
    print(response)


def addCabinet(name, sup, data):
    response = sup.table("Cabinets").insert({"name": name}).execute()
    data.CABINETS = getCabinets(sup=sup)
    print(response)


def getGroups(sup):
    data, count = sup.table("Groups").select('id', 'name').execute()
    return [Group(item['id'], item['name']) for item in data[1]]


def getSubs(sup):
    data, count = sup.table("MessagingClients").select('*').execute()
    return [Subscriber(item['id'] ,item['token']  ,item['clientID'],item['subType'],   item['subID']) for item in data[1]]


def getParaNameAndTeacher(para,data):
    logger.info(para)
    if (para != '' and para != None):
        temp = para.replace('\n', ' ').replace('\t', ' ')
        ParaMonday = re.sub(r' {2,}', ' ', temp)
        if (not ParaMonday.__contains__("Резерв")):
            sample = ParaMonday.replace('.','').replace(' ','').lower()
            finded_teachers = get_teachers_from_string(teachers=data.TEACHERS,shortName=sample)
            if len(finded_teachers) == 1:
                return [finded_teachers[0].name, sample.replace(finded_teachers[0].name.replace(' ','').replace('.','').lower(),'')]
            if len(finded_teachers) > 1:
                course_text = sample
                for i in finded_teachers:
                    temp = i.name.split(' ')
                    short_fio = f"{temp[0]}{temp[1][0]}{temp[2][0]}".lower()
                    course_text = course_text.replace(short_fio, '')
                return [finded_teachers[0].name,course_text]
            try:
                prepodMonday = f"{sample[-3]} {sample[-2]} {sample[-1]}"
            except:
                try:
                    prepodMonday = f"{sample[-2]} {sample[-1]}"
                except:
                    try:
                        prepodMonday = f"{sample[-1]}"
                    except:
                        prepodMonday = f"{sample}"
        else:
            if len(ParaMonday.split(' ')) > 3:
                sample = ParaMonday.split(' ')
                prepodMonday = f"{sample[-3]} {sample[-2]}"
                return [prepodMonday, re.sub(r' {2,}', ' ', ParaMonday.replace(prepodMonday, '').strip())]
            else:
                prepodMonday = ParaMonday.split(' ')[-1]
        res = [prepodMonday.strip(), ParaMonday.replace(prepodMonday, '').strip()]
        print(f"RESULT {res}")
        return [prepodMonday.strip(), ParaMonday.replace(prepodMonday, '').strip()]


def getTeachers(sup):
    data, count = sup.table("Teachers").select('id', 'name').execute()
    return [Teacher(item['id'], item['name']) for item in data[1]]


def getCabinets(sup):
    data, count = sup.table("Cabinets").select('id', 'name').execute()
    return [Cabinet(item['id'], item['name']) for item in data[1]]


def getCourses(sup):
    data, count = sup.table("Courses").select('id', 'name').execute()
    return [Course(item['id'], item['name']) for item in data[1]]


def addZamena(sup, group, number, course, teacher, cabinet, date):
    response = sup.table("Zamenas").insert(
        {"group": group, 'number': int(number), 'course': course, 'teacher': teacher, 'cabinet': cabinet,
         'date': str(date)}).execute()
    print(response)


def addZamenas(sup, zamenas):
    response = sup.table("Zamenas").insert(zamenas).execute()
    print(response)


def add_practices(sup, practices):
    response = sup.table("Practices").insert(practices).execute()
    print(response)


def addFullZamenaGroup(sup, group, date):
    response = sup.table("ZamenasFull").insert({"group": group, 'date': str(date)}).execute()
    print(response)


def addFullZamenaGroups(sup, groups):
    response = sup.table("ZamenasFull").insert(groups).execute()
    print(response)


def addHoliday(sup, date, name):
    response = sup.table("Holidays").insert({"name": name, 'date': str(date)}).execute()
    print(response)


def addLiquidation(sup, group, date):
    response = sup.table("Liquidation").insert({"group": group, 'date': str(date)}).execute()
    print(response)


def addLiquidations(sup, liquidations):
    response = sup.table("Liquidation").insert(liquidations).execute()
    print(response)


def parse(link, date : datetime.date, sup):
    data = Data
    data.GROUPS = getGroups(sup=sup)
    data.CABINETS = getCabinets(sup=sup)
    data.TEACHERS = getTeachers(sup=sup)
    data.COURSES = getCourses(sup=sup)
    filename = f"zam-{date.year}-{date.month}-{date.day}"
    response = requests.get(link)
    if response.status_code == 200:
        with open(f"{filename}.pdf", 'wb') as file:
            file.write(response.content)
            file.flush()
    else:
        raise Exception("Файл не загружен")
    cv = Converter(f'{filename}.pdf')
    cv.convert(f'{filename}.docx', start=0, end=None)
    cv.close()
    parseZamenas(f"{filename}.docx", date, sup=sup, data=data,link=link)
    try:
        if(os.path.isfile(f"{filename}.pdf")):
            os.remove(f"{filename}.pdf")
        if (os.path.isfile(f"{filename}.docx")):
            os.remove(f"{filename}.docx")
    except Exception as error:
        print(error)