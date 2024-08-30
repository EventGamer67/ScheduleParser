import logging
import os
import random
from typing import List
import requests
import supabase
from pdf2docx import *
from datetime import datetime
from supabase import create_client, Client
from parser_secrets import SUPABASE_URL, SUPABASE_ANON_KEY
from src.code.models.cabinet_model import Cabinet
from src.code.models.course_model import Course
from src.code.models.data_model import Data
from src.code.models.group_model import Group
from src.code.models.parsed_date_model import ParsedDate
from src.code.models.subscriber_model import Subscriber
from src.code.models.teacher_model import Teacher
from src.code.tools.logs import logger

class SupaBaseWorker:
    def __init__(self) -> None:
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    @staticmethod
    def get_groups_from_string(self, string: str, data_model: Data) -> list[Group]:
        """
        Возвращает коллекцию объектов Group на основе поисковой строки и модели

        :param поисковая строка string:
        :param модель data_model:
        """
        groups = []
        for gr in data_model.GROUPS:
            if (string.lower().strip().__contains__(gr.name.lower().strip())):
                groups.append(gr)
        return groups

    def getParsedsHashes(self):
        """
        Получает хэши из БД
        """
        client = self.client
        response: supabase.PostgrestAPIResponse = client.from_('parseddays').select('hash').execute()
        hashes = list()

        for item in response.data:
            hashes.append(item['hash'])
        return hashes


    def addPara(self, group, number, course, teacher, cabinet, date):
        """
        Добавляет пару на основе значений переданных в метод

        :param группа group:
        :param номер пары number:
        :param курс course:
        :param препод teacher:
        :param кабинет cabinet:
        :param дата date:
        """
        client = self.client
        client.table('Paras').insert(
            {'group': group, 'number': number, 'course': course, 'teacher': teacher, 'cabinet': cabinet,
            'date': date}).execute()
        pass


    def addNewZamenaFileLink(self, link: str, date: datetime, hash: str):
        """
        Добавляет ссылку на новый файл с заменами

        :param ссылка на файk link:
        :param дата файла date:
        :param хеш файла hash:
        """
        client = self.client
        response = client.table("ZamenaFileLinks").insert({"link": link, "date": str(date), "hash":hash}).execute()
        return response


    def get_zamena_file_links(self) -> List[ParsedDate]:
        """
        Возвращает коллекцию со списком спарсенных файлов
        """
        client = self.client
        response = client.table("ZamenaFileLinks").select('*').execute()
        parsed_days: List[ParsedDate] = []
        for i in response.data:
            parsed_days.append(ParsedDate(date=i["date"],link=i["link"],filehash=i["hash"]))
        return parsed_days

    @property
    def get_data_models_list(self) -> tuple[list[Group], list[Subscriber],
                                            list[Teacher], list[Cabinet], list[Course]]:
        """
        Возвращает кортеж данных с информацией о группах, подписчиках, преподах, кабинетов и курсах
        """
        return self._getGroups(), self._getSubs(), self._getTeachers(), self._getCabinets(), self._getCourses()

    def addZamena(self, group, number, course, teacher, cabinet, date):
        client = self.client
        response = client.table("Zamenas").insert(
            {"group": group, 'number': int(number), 'course': course, 'teacher': teacher, 'cabinet': cabinet,
            'date': str(date)}).execute()
        print(response)

    def addZamenas(self, zamenas):
        client = self.client
        response = client.table("Zamenas").insert(zamenas).execute()
        print(response)

    def add_practices(self, practices):
        client = self.client
        response = client.table("Practices").insert(practices).execute()
        print(response)

    def addFullZamenaGroup(self, group, date):
        client = self.client
        response = client.table("ZamenasFull").insert({"group": group, 'date': str(date)}).execute()
        print(response)

    def addFullZamenaGroups(self, groups):
        client = self.client
        response = client.table("ZamenasFull").insert(groups).execute()
        print(response)

    def addHoliday(self, date, name):
        client = self.client
        response = client.table("Holidays").insert({"name": name, 'date': str(date)}).execute()
        print(response)

    def addLiquidation(self, group, date):
        client = self.client
        response = client.table("Liquidation").insert({"group": group, 'date': str(date)}).execute()
        print(response)

    def addLiquidations(self, liquidations):
        client = self.client
        response = client.table("Liquidation").insert(liquidations).execute()
        print(response)

    def addGroup(self, name, data_model: Data):
        client = self.client
        response = client.table("Groups").insert({"name": name, "department": 0}).execute()
        data_model.GROUPS = self._getGroups(client=client)
        print(response)

    def addCourse(self, name, data_model: Data):
        client = self.client
        rnd = random.Random()
        color = f'{255},{rnd.randint(0, 255)},{rnd.randint(0, 255)},{rnd.randint(0, 255)}'
        response = client.table("Courses").insert({"name": name, "color": color}).execute()
        data_model.COURSES = self._getCourses(client=client)
        print(response)

    def addTeacher(self, name, data_model: Data):
        client = self.client
        response = client.table("Teachers").insert({"name": name}).execute()
        data_model.TEACHERS = self._getTeachers(client=client)
        print(response)

    def addCabinet(self, name, data_model: Data):
        client = self.client
        response = client.table("Cabinets").insert({"name": name}).execute()
        data_model.CABINETS = self._getCabinets(client=client)
        print(response)

    def _getGroups(self):
        client = self.client
        data, _ = client.table("Groups").select('id', 'name').execute()
        return [Group(item['id'], item['name']) for item in data[1]]

    def _getSubs(self):
        client = self.client
        data, _ = client.table("MessagingClients").select('*').execute()
        return [Subscriber(item['id'], item['token'], item['clientID'], item['subType'], item['subID']) for item in data[1]]

    def _getTeachers(self):
        client = self.client
        data, _ = client.table("Teachers").select('id', 'name').execute()
        return [Teacher(item['id'], item['name']) for item in data[1]]


    def _getCabinets(self):
        client = self.client
        data, _ = client.table("Cabinets").select('id', 'name').execute()
        return [Cabinet(item['id'], item['name']) for item in data[1]]


    def _getCourses(self):
        client = self.client
        data, _ = client.table("Courses").select('id', 'name').execute()
        return [Course(item['id'], item['name']) for item in data[1]]
