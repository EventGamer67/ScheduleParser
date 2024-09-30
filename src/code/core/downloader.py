import asyncio
import os
import urllib
import docx.shared
import fitz
import requests
import re
from pdf2docx import Converter
from urllib.request import urlopen


# SCHEDULE_URL = 'https://www.uksivt.ru/zameny'
# # SCHEDULE_URL = 'http://127.0.0.1:3000/c:/Users/Danil/Desktop/Uksivt/sample.html'

# BASEURL = 'https://www.uksivt.ru/'


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


# def parse_teacher_schedule():
#     # cv = Converter(f'test.pdf')
#     # cv.convert(f'test' + '.docx')
#     # cv.close()
#     doc = Document('test.docx')
#     for i in doc.paragraphs:
#         print(i.text)


# def parseZamenas(filename: str, date, sup, data, link:str):
#     all_rows, header = get_all_tables(filename)

#     practice_groups: List[Group] = []
#     for i in header:
#         practice_groups.extend(supabase_worker.get_groups_from_string(i.text, data=data))

#     workRows = []
#     for i in all_rows:
#         if (not is_nested(i)):
#             workRows.extend(i)
#         else:
#             workRows.append(i)

#     # test cleaning before ликвидация замен
#     temp = []

#     for i in workRows:
#         if len(i) == 7:
#             temp.append(i)

#     workRows = temp

#     for i in workRows:
#         if i[2] == '' and i[3] != '':
#             i[3] = ''
#         if i[1] == '' and i[2] == '' and i[3] == '' and i[5] == '':
#             i[4] = ''
#             pass

#     workRows = clearNonDataRows(workRows)
#     workRows = clear_empty_sublists(workRows)
#     workRows = remove_headers(workRows)
#     workRows = removeDemoExam(workRows)

#     fullzamenagroups = []
#     liquidation = []
#     iteration = 0

#     for i in workRows:
#         iteration = iteration + 1
#         if i[0] == '':
#             i[0] = workRows[iteration - 2][0]

#     for i in workRows[:]:
#         if i[0] == i[1] and i[2] == i[3]:
#             if (i[0].strip().lower().__contains__("ликвидация")):
#                 try:
#                     sample = i[0].strip().lower()
#                     for gr in data.GROUPS:
#                         if (sample.__contains__(gr.name.lower().strip())):
#                             liquidation.append(gr.id)
#                             print(f"Ликвидация {gr.name}")
#                 except Exception as err:
#                     print(err)
#                     continue
#                 workRows.remove(i)

#     for i in workRows[:]:
#         i.pop(2)

#     for i in workRows[:]:
#         i.pop(2)

#     for i in workRows[:]:
#         if (i[1] == '' and i[2] == '' and i[3] == '' and i[4] == ''):
#             workRows.remove(i)

#     for i in workRows[:]:
#         if i[0] == i[1] and i[1] == i[2] and i[2] == i[3] and i[3] == i[4]:
#             fullzamenagroups.append(i[0].strip().replace(' ', ""))
#             workRows.remove(i)

#     #чистка столбца группы
#     #удаляет лишние -, пробелы, запятые, точки и приводит к uppercase
#     cleaned_groups_workrows = []
#     for i in workRows:
#         i[0] = i[0].replace(' ','').replace(',','').replace('.','').upper()
#         i[0] = re.sub(r'-{2,}', '-', i[0])

#     editet = []
#     for i in workRows:
#         try:
#             text = i[1].replace('.',',')
#             print(text)
#             if text[-1] == ',':
#                 text = text[0:-1]
#                 i[1] = text
#             if text[0] == ',':
#                 text = text[0:len(text) - 1]
#                 i[1] = text
#             paras = i[1].replace('.',',').split(',')
#             row = i.copy()
#             if (len(paras) >= 2):
#                 for para in paras:
#                     new = row.copy()
#                     new[1] = para
#                     editet.append(new)
#             else:
#                 editet.append(i)
#         except Exception as error:
#             print(error)
#             print(i)
#             continue
#     workRows = editet

#     for i in workRows:
#         print(i)

#     for row in workRows:
#         group = get_group_by_id(data.GROUPS, row[0], sup=sup, data=data)
#         if group is not None:
#             row[0] = group.id

#     for row in workRows:
#         print(row[2])
#         course = get_course_by_id(data.COURSES, row[2], sup=sup, data=data)
#         if course is not None:
#             row[2] = course.id

#     for row in workRows:
#         print(row[3])
#         teacher = get_teacher_by_id(data.TEACHERS, row[3], sup=sup, data=data)
#         if teacher is not None:
#             row[3] = teacher.id

#     for row in workRows:
#         cabinet = get_cabinet_by_id(data.CABINETS, row[4], sup=sup, data=data)
#         if cabinet is not None:
#             row[4] = cabinet.id

#     practice_supabase = []
#     for i in practice_groups:
#         practice_supabase.append({"group": i.id, 'date': str(date)})
#         pass

#     zamenas_supabase = []
#     for i in workRows:
#         print(f"zamena {i}")
#         zamenas_supabase.append(
#             {"group": i[0], 'number': int(i[1]), 'course': i[2], 'teacher': i[3], 'cabinet': i[4], 'date': str(date)})
#         pass

#     full_zamenas_groups = []
#     for i in fullzamenagroups:
#         full_zamenas_groups.append({"group": get_group_by_id(target_name=i, data=data, groups=data.GROUPS, sup=sup).id, 'date': str(date)})
#         pass

#     liquidations = []
#     for i in liquidation:
#         liquidations.append({"group": i, 'date': str(date)})
#         pass

#     supabase_worker.addZamenas(sup=sup, zamenas=zamenas_supabase)
#     if len(full_zamenas_groups) > 0:
#         supabase_worker.addFullZamenaGroups(sup=sup, groups=full_zamenas_groups)
#         pass
#     if len(practice_supabase) > 0:
#         supabase_worker.add_practices(sup=sup, practices=practice_supabase)
#         pass
#     if len(liquidations) > 0:
#         supabase_worker.addLiquidations(sup=sup, liquidations=liquidations)
#         pass
#     hash = get_remote_file_hash(link)
#     supabase_worker.addNewZamenaFileLink(link,date=date,sup=sup, hash=hash)
#     pass



