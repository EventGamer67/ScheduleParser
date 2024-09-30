import asyncio
import datetime
import html
import logging
import sys
import traceback
from urllib.request import urlopen

from aiogram.enums import ParseMode
from celery import Celery
from celery.result import AsyncResult
import pytz
import requests
from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage import redis
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bs4 import BeautifulSoup
from typing import List

from docx2pdf import convert

from bot_worker import parse_zamenas, parse_schedule
from parser_secrets import *
from src import *
from src.code.core.downloader import create_pdf_screenshots, cleanup_temp_files
from src.code.core.schedule_parser import getAllMonthTables, getAllTablesLinks, downloadFile, getLastZamenaLink
from src.code.models.data_model import Data
from src.code.models.parsed_date_model import ParsedDate
from src.code.models.zamena_table_model import ZamTable
from src.code.network.supabase_worker import SupaBaseWorker
from src.code.tools.functions import get_remote_file_hash, get_file_extension
from src.firebase.firebase import send_message_to_topic

sup = SupaBaseWorker()
dp = Dispatcher()
router = Router()
admins = [1283168392]
r = redis.Redis(host=REDIS_HOST_URL, port=REDIS_PORT, decode_responses=True, password=REDIS_PASSWORD,
                username=REDIS_USERNAME)


celery_app = Celery(
    'telegram_bot',
    broker='amqp://guest:guest@127.0.0.1:5672//',  # Используйте 127.0.0.1 для RabbitMQ
    backend='redis://127.0.0.1:6379/0'             # Используйте 127.0.0.1 для Redis
)


async def on_on(bot: Bot):
    await bot.send_message(chat_id=admins[0], text='включен')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🐋", url="https://uksivt.xyz/")]])
    tz = pytz.timezone('Asia/Yekaterinburg')
    times = datetime.datetime.now(tz=tz)
    hours = times.strftime("%H")
    mins = times.strftime("%M")
    res = await bot.edit_message_text(
        f"🟢 🌊 uksivt.xyz\nПоиск по группам, преподам и кабинетам\nвключен {f'{hours}:{mins} {times.day}.{times.month}'}",
        chat_id=-1002035415883, message_id=80, reply_markup=keyboard)


async def on_exit(bot: Bot):
    await bot.send_message(chat_id=admins[0], text='выключен')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🐋", url="https://uksivt.xyz/")]])
    tz = pytz.timezone('Asia/Yekaterinburg')
    times = datetime.datetime.now(tz=tz)
    hours = times.strftime("%H")
    mins = times.strftime("%M")
    res = await bot.edit_message_text(
        f"💤 🌊 uksivt.xyz\nПоиск по группам, преподам и кабинетам\nвыключен {f'{hours}:{mins} {times.day}.{times.month}'}",
        chat_id=-1002035415883, reply_markup=keyboard, message_id=80)


async def on_check(bot: Bot):
    # await bot.send_message(chat_id=admins[0], text='проверил')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🐋", url="https://uksivt.xyz/")]])
    tz = pytz.timezone('Asia/Yekaterinburg')
    times = datetime.datetime.now(tz=tz)
    hours = times.strftime("%H")
    mins = times.strftime("%M")
    res = await bot.edit_message_text(
        f"🟢 Последняя проверка {f'{hours}:{mins} {times.day}.{times.month}'}\nuksivt.xyz Поиск по группам, преподам и кабинетам",
        chat_id=-1002035415883, message_id=80, reply_markup=keyboard)


async def checkNew(bot: Bot):
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    tables: List[ZamTable] = getAllMonthTables(soup=soup)
    site_links = getAllTablesLinks(tables)
    databaseLinks: List[ParsedDate] = sup.get_zamena_file_links()
    await on_check(bot=bot)
    if site_links.__eq__(databaseLinks):
        pass
    else:
        alreadyFound = await r.lrange("alreadyFound", 0, -1)
        new = list(set(site_links) - set([x.link for x in databaseLinks]) - set(alreadyFound))
        new.reverse()
        if (len(new) < 1):
            for i in tables[0].zamenas:
                if (i.date > datetime.date.today()):
                    hash = get_remote_file_hash(i.link)
                    try:
                        print("here3")
                        print(databaseLinks[-1].link)
                        print(i.link)
                        oldhash = [x for x in databaseLinks if x.link == i.link][0].hash
                        print("here4")
                        if hash != oldhash:
                            await bot.send_message(chat_id=admins[0], text=f'Обнаружен перезалив на {i.link} {i.date}')
                            extension = get_file_extension(i.link)
                            filename = i.link.split('/')[-1].split('.')[0]
                            downloadFile(link=i.link, filename=f"{filename}.{extension}")
                            if extension == 'pdf':
                                screenshot_paths = await create_pdf_screenshots(filename)
                            if extension == 'docx':
                                convert(f"{filename}.{extension}")
                                screenshot_paths = await create_pdf_screenshots(filename)
                            media_group = MediaGroupBuilder(
                                caption=f"Перезалив замен на <a href='{i.link}'>{i.date}</a>  ")

                            for j in screenshot_paths:
                                image = FSInputFile(j)
                                media_group.add_photo(image)
                            try:

                                await bot.send_media_group(-1002035415883, media=media_group.build())
                                send_message_to_topic( 'Перезалив замен',
                                                      f'Обнаружен перезалив замен на {i.date}',sup=sup)
                            except Exception as error:
                                await bot.send_message(chat_id=admins[0], text=str(error))
                            subs = await r.lrange("subs", 0, -1)
                            for j in subs:
                                try:
                                    await bot.send_media_group(j, media=media_group.build())
                                except Exception as error:
                                    try:
                                        await bot.send_message(chat_id=admins[0], text=str(error))
                                    except:
                                        continue
                            cleanup_temp_files(screenshot_paths)
                            os.remove(f"{filename}.pdf")
                            datess = datetime.datetime(year=i.date.year, month=i.date.month, day=i.date.day)
                            sup.table('Zamenas').delete().eq('date', datess).execute()
                            sup.table('ZamenasFull').delete().eq('date', datess).execute()
                            res = sup.table('ZamenaFileLinks').update({'hash': hash}).eq('link', i.link).execute()
                            await bot.send_message(chat_id=admins[0], text=f'Обновлен хеш {res}')
                            parse_zamenas(url=i.link, date_=datess)
                            await bot.send_message(chat_id=admins[0], text='parsed')
                    except Exception as error:
                        print(error)
                        await bot.send_message(chat_id=admins[0], text=str(error.__str__()))
            return
        for link in new:
            zam = [x for x in tables if x.links.__contains__(link)][0]
            zamm = [x for x in zam.zamenas if x.link == link][0]
            try:
                await r.lpush("alreadyFound", str(zamm.link))
                if (link.__contains__('google.com') or link.__contains__('yadi.sk')):
                    continue
                extension = get_file_extension(zamm.link)
                filename = zamm.link.split('/')[-1].split('.')[0]
                downloadFile(link=zamm.link, filename=f"{filename}.{extension}")
                if extension == 'pdf':
                    screenshot_paths = await create_pdf_screenshots(filename)
                if extension == 'docx':
                    convert(f"{filename}.{extension}")
                    screenshot_paths = await create_pdf_screenshots(filename)
                media_group = MediaGroupBuilder(caption=f"Новые замены на <a href='{zamm.link}'>{zamm.date}</a>  ")
                for i in screenshot_paths:
                    image = FSInputFile(i)
                    media_group.add_photo(image)
                try:
                    # await bot.send_media_group(chat_id=admins[0], media=media_group.build())
                    await bot.send_media_group(-1002035415883, media=media_group.build())
                    send_message_to_topic( 'Новые замены', f'Новые замены на {zamm.date}',sup=sup)
                except Exception as error:
                    await bot.send_message(chat_id=admins[0], text=str(error))
                subs = await r.lrange("subs", 0, -1)
                for i in subs:
                    try:
                        await bot.send_media_group(i, media=media_group.build())
                    except Exception as error:
                        try:
                            await bot.send_message(chat_id=admins[0], text=str(error))
                        except:
                            continue
                cleanup_temp_files(screenshot_paths)
                os.remove(f"{filename}.pdf")
                datess = datetime.date(zamm.date.year, zamm.date.month, zamm.date.day)
                sup.table('Zamenas').delete().eq('date', datess).execute()
                sup.table('ZamenasFull').delete().eq('date', datess).execute()
                sup.table('ZamenaFileLinks').delete().eq('date', datess).execute()
                parse_zamenas(url=zamm.link, date_=datess)
                await bot.send_message(chat_id=admins[0], text='parsed')
            except Exception as error:
                await bot.send_message(chat_id=admins[0], text=f'{str(error)}\n{str(error.__traceback__)}')


@dp.message(F.text, Command("update"))
async def my_update(messsage: Message):
    if messsage.chat.id in admins:
        await  messsage.reply("Проверяю")
        await checkNew(bot=messsage.bot)
        await messsage.reply("Проверил")


@dp.message(F.text, Command("alert"))
async def my_alert(messsage: Message):
    if messsage.chat.id in admins:
        try:
            send_message_to_topic(messsage.text.split(' ')[1], messsage.text.split(' ')[2], sup=sup)
            await messsage.reply("Отправил")
        except Exception as e:
            await messsage.answer(f"Ошибка \n{e}")



@dp.message(F.text, Command("sub"))
async def my_handlerr(message: Message):
    try:
        list = await r.lrange("subs", 0, -1)
        if str(message.chat.id) not in list:
            await r.lpush("subs", message.chat.id)
            await message.answer("Подписан")
        else:
            await message.answer("Вы уже подписаны")
    except Exception as error:
        await message.answer(f"Ошибка подписки\n{error}")


@dp.message(F.text, Command("unsub"))
async def my_handlers(message: Message):
    try:
        await r.lrem("subs", 0, message.chat.id)
        await message.answer("Отписан")
    except Exception as error:
        await message.answer(f"Ошибка отписки\n{error}")


@dp.message(F.text, Command("holiday"))
async def my_handlers(message: Message):
    if message.chat.id in admins:
        try:
            date = message.text.split(' ')[1]
            name = message.text.split(' ')[2]
            date = datetime.date(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]))
            response = sup.table("Holidays").insert({"name": name, 'date': str(date)}).execute()
            await  message.answer(f'holiday set {response}')
        except Exception as err:
            await message.answer(str(err))


@dp.message(F.text, Command("remove"))
async def my_handlers(message: Message):
    if message.chat.id in admins:
        try:
            date = message.text.split(' ')[1]
            date = datetime.date(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]))
            deleted = []
            deleted.append(sup.table('Zamenas').delete().eq('date', date).execute())
            deleted.append(sup.table('ZamenasFull').delete().eq('date', date).execute())
            deleted.append(sup.table('ZamenaFileLinks').delete().eq('date', date).execute())
            await message.answer(f'deleted {deleted[0:10]}')
        except Exception as err:
            await message.answer(str(err))


@dp.message(F.text, Command("parse"))
async def my_handlers(message: Message):
    if message.chat.id in admins:
        try:
            date = message.text.split(' ')[1]
            date = datetime.date(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]))
            link = message.text.split(' ')[2]
            parse_schedule(url=link, date_=date)
            await message.answer(f'parsed')
        except Exception as error:
            await message.answer(text=f'{str(error)}\n{traceback.format_exc()}')


@dp.message(F.text, Command("paras"))
async def my_handlers(message: Message):
    if message.chat.id in admins:
        try:
            date = message.text.split(' ')[1]
            date = datetime.date(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]))
            link = message.text.split(' ')[2]
            # data = Data(sup=sup)
            # filename = f"zam-{date.year}-{date.month}-{date.day}"
            # response = requests.get(link)
            # if response.status_code == 200:
            #     with open(f"{filename}.pdf", 'wb') as file:
            #         file.write(response.content)
            #         file.flush()
            # else:
            #     raise Exception("Файл не загружен")
            parse_schedule(url=link, date_=date)
            # try:
            #     if (os.path.isfile(f"{filename}.pdf")):
            #         os.remove(f"{filename}.pdf")
            #     if (os.path.isfile(f"{filename}.docx")):
            #         os.remove(f"{filename}.docx")
            # except Exception as error:
            #     await message.answer(str(error))
            await message.answer(f'parsed')
        except Exception as error:
            await message.answer(text=f'{str(error)}\n{traceback.format_exc()}')


@dp.message(F.text, Command("latest"))
async def my_handler(message: Message):
    if message.chat.id in admins:
        html = urlopen(SCHEDULE_URL).read()
        soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
        link, date = getLastZamenaLink(soup=soup)
        await message.answer(f"{link} {date}")

#
# @dp.message(F.text, Command("merge_cab"))
# async def my_handler(message: Message):
#     if message.chat.id in admins:
#         merge_from = message.text.split()[1]
#         merge_to = message.text.split()[2]
#         data = sup.table('Paras').update({'cabinet': merge_to}).eq('cabinet', merge_from).execute()
#         print(data)
#         count = len(data.data)
#         data = sup.table('Zamenas').update({'cabinet': merge_to}).eq('cabinet', merge_from).execute()
#         print(data)
#         count = count + len(data.data)
#         sup.table('Cabinets').delete().eq('id', merge_from).execute()
#         await message.answer(f"Поменял с {merge_from} на {merge_to} | {count} раз")
#
#
# @dp.message(F.text, Command("merge_teacher"))
# async def my_handler(message: Message):
#     if message.chat.id in admins:
#         merge_from = message.text.split()[1]
#         merge_to = message.text.split()[2]
#         data = sup.table('Paras').update({'teacher': merge_to}).eq('teacher', merge_from).execute()
#         print(data)
#         count = len(data.data)
#         data = sup.table('Zamenas').update({'teacher': merge_to}).eq('teacher', merge_from).execute()
#         print(data)
#         count = count + len(data.data)
#         sup.table('Teachers').delete().eq('id', merge_from).execute()
#         await message.answer(f"Поменял с {merge_from} на {merge_to} | {count} раз")


async def main() -> None:
    bot = Bot(SCHEDULE_PARSER_TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    scheduler = AsyncIOScheduler()
    #trigger = CronTrigger(minute='0/15', hour='2-17')
    #scheduler.add_job(checkNew, trigger, args=(bot,))
    scheduler.start()
    try:
        await on_on(bot=bot)
        #await checkNew(bot=bot)
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await on_exit(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())