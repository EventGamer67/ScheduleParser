"""
Модуль описывающий работу бота телеграм
"""


import magic
import requests
from io import BytesIO
from http import HTTPStatus
from datetime import date
from pdf2docx import Converter
from src.code.core.parser import parseZamenas
from src.code.network.supabase_worker import SupaBaseWorker
from src.code.models.data_model import Data


def _init_date_model() -> Data:
    data_model = Data
    supabase_client = SupaBaseWorker()

    data_model.GROUPS, _, data_model.CABINETS, data_model.TEACHERS, _, data_model.COURSES = supabase_client.get_data_models_list
    return data_model


def _get_file_stream(link: str) -> BytesIO:
    response = requests.get(link)

    if response.status_code == HTTPStatus.OK.value:
        with BytesIO() as stream:
            stream.write(response.content)
    else:
        raise Exception("Данные не получены")
    return stream

def _define_file_format(data: bytes):
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(data)

    return file_type

def parse(link: str, date_: date):
    data_model = _init_date_model()
    stream = _get_file_stream(link=link)
    file_type = _define_file_format(stream.read())

    match file_type:
        case 'application/pdf':
            cv = Converter(stream.read())
            stream_converted = BytesIO()

            cv.convert(stream_converted)
            cv.close()

            parseZamenas(stream_converted, date_, data_model, link)
        case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            parseZamenas(stream, date_, data_model, link)
