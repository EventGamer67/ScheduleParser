"""
Модуль харнит в себе методы по работе со строкой полученнной из БД
"""

import re
from src.code.models.data_model import Data
from src.code.models.teacher_model import Teacher
from src.code.core.downloader import parseZamenas, get_teacher_from_short_name, get_teachers_from_string


def getParaNameAndTeacher(para: str, data_model: Data) -> None | list[str]:
    if not para:
        return None

    temp = para.replace('\n', ' ').replace('\t', ' ')
    ParaMonday = re.sub(r' {2,}', ' ', temp)

    if "Резерв" in ParaMonday:
        return _handle_reserved(ParaMonday)

    sample = ParaMonday.replace('.', '').replace(' ', '').lower()
    finded_teachers = get_teachers_from_string(teachers=data_model.TEACHERS, shortName=sample)

    if len(finded_teachers) == 1:
        return [finded_teachers[0].name, _clean_teacher_name(sample, finded_teachers[0].name)]

    if len(finded_teachers) > 1:
        return _handle_multiple_teachers(finded_teachers, sample)

    return _handle_excpetions_teacher(sample, ParaMonday)


def _clean_teacher_name(sample: str, teacher_name: str):
    return sample.replace(teacher_name.replace(' ', '').replace('.', '').lower(), '')


def _handle_multiple_teachers(finded_teachers: list[Teacher], sample: str):
    course_text = sample
    for teacher in finded_teachers:
        temp = teacher.name.split(' ')
        short_fio = f"{temp[0]}{temp[1][0]}{temp[2][0]}".lower()
        course_text = course_text.replace(short_fio, '')
    return [finded_teachers[0].name, course_text]


def _handle_reserved(ParaMonday: str):
    parts = ParaMonday.split(' ')
    if len(parts) > 3:
        prepodMonday = f"{parts[-3]} {parts[-2]}"
        remainder = re.sub(r' {2,}', ' ', ParaMonday.replace(prepodMonday, '').strip())
        return [prepodMonday, remainder]
    else:
        prepodMonday = parts[-1]
        return [prepodMonday, ParaMonday.replace(prepodMonday, '').strip()]


def _handle_excpetions_teacher(sample, ParaMonday):
    try:
        prepodMonday = f"{sample[-3]} {sample[-2]} {sample[-1]}"
    except IndexError:
        try:
            prepodMonday = f"{sample[-2]} {sample[-1]}"
        except IndexError:
            try:
                prepodMonday = f"{sample[-1]}"
            except IndexError:
                prepodMonday = sample

    res = [prepodMonday.strip(), ParaMonday.replace(prepodMonday, '').strip()]
    print(f"RESULT {res}")
    return res
