import json
import random
from datetime import datetime

import supabase
from supabase import create_client, Client

from main import Data
from models import Group, Course, Cabinet, Teacher


def initSupabase():
    supabase: Client = create_client("https://ojbsikxdqcbuvamygezd.supabase.co",
                                     "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9qYnNpa3hkcWNidXZhbXlnZXpkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDE4MDY4OTgsImV4cCI6MjAxNzM4Mjg5OH0.jV7YiBEePGjybsL8qqXWeQ9PX8_3yctpq14Gfwh39JM")
    return supabase


def getParsedsHashes():
    supa = initSupabase()
    response: supabase.APIResponse = supa.from_('parseddays').select('hash').execute()
    hashes = []
    for item in response.data:
        hashes.append(item['hash'])

    return hashes


def addPara(sup : Client,group,number,course,teacher,cabinet,date):
    sup.table('Paras').insert({'group':group,'number':number,'course':course,'teacher':teacher,'cabinet':cabinet,'date':date}).execute()
    pass

def addNewZamenaFileLink(link: str, date):
    sup = initSupabase()
    response = sup.table("ZamenaFileLinks").insert({"link":link,"date":str(date)}).execute()
    return response


def addGroup(name,sup,data:Data):
    response = sup.table("Groups").insert({"name":name,"department":0}).execute()
    data.GROUPS = getGroups(sup=sup)
    print(response)


def addCourse(name,sup,data:Data):
    rnd = random.Random()
    color = f'{255},{rnd.randint(0, 255)},{rnd.randint(0, 255)},{rnd.randint(0, 255)}'
    response = sup.table("Courses").insert({"name":name,"color":color}).execute()
    data.COURSES = getCourses(sup=sup)
    print(response)


def addTeacher(name,sup,data:Data):
    response = sup.table("Teachers").insert({"name":name}).execute()
    data.TEACHERS = getTeachers(sup=sup)
    print(response)


def addCabinet(name,sup,data:Data):
    response = sup.table("Cabinets").insert({"name":name}).execute()
    data.CABINETS = getCabinets(sup=sup)
    print(response)


def getGroups(sup):
    data, count = sup.table("Groups").select('id','name').execute()
    return [Group(item['id'], item['name']) for item in data[1]]

def getParaNameAndTeacher(para):
    if (para != ''):
        ParaMonday = para.replace('\n', ' ')
        prepodMonday = ''
        if (not ParaMonday.__contains__("Резерв")):
            sample = ParaMonday.split(' ')
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
            prepodMonday = ParaMonday.split(' ')[-1]
        return [prepodMonday.strip(), ParaMonday.replace(prepodMonday, '').strip()]

def getTeachers(sup):
    data, count = sup.table("Teachers").select('id','name').execute()
    return [Teacher(item['id'], item['name']) for item in data[1]]


def getCabinets(sup):
    data, count = sup.table("Cabinets").select('id','name').execute()
    return [Cabinet(item['id'], item['name']) for item in data[1]]

def getCourses(sup):
    data, count = sup.table("Courses").select('id','name').execute()
    return [Course(item['id'], item['name']) for item in data[1]]

def addZamena(sup,group,number,course,teacher,cabinet,date):
    response = sup.table("Zamenas").insert({"group": group,'number':int(number),'course':course,'teacher':teacher,'cabinet':cabinet,'date':str(date)}).execute()
    print(response)


def addFullZamenaGroup(sup,group,date):
    response = sup.table("ZamenasFull").insert({"group": group,'date':str(date)}).execute()
    print(response)