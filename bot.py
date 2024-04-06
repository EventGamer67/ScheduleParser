import asyncio
import logging
import os
import sys
import traceback
from typing import List
from urllib.request import urlopen
import datetime
from aiogram.fsm.storage import redis
from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, MessageEntity, InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from classes import ZamTable
from downloader import getLastZamenaLink, SCHEDULE_URL, getAllMonthTables, getAllTablesLinks, create_pdf_screenshots, cleanup_temp_files, downloadFile
from functions import get_file_extension
from supbase import initSupabase, GetZamenaFileLinks, parse
from aiogram.types import FSInputFile
import pytz
from docx2pdf import convert

TOKEN = "5261332325:AAEVl8ACJvWB4Pajhm3HHKkklPjCjoVQr_o"
sup = initSupabase()
dp = Dispatcher()
router = Router()
admins = [1283168392]
r = redis.Redis(host='monorail.proxy.rlwy.net', port=13877, decode_responses=True,
                    password="BNFODHMBEaF3fdNd4akOD2CPg5HgEMla", username="default")


async def on_on(bot: Bot):
    await bot.send_message(chat_id=admins[0], text='включен')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🐋", url="https://uksivt.xyz/")]])
    tz = pytz.timezone('Asia/Yekaterinburg')
    times = datetime.datetime.now(tz=tz)
    hours = times.strftime("%H")
    mins = times.strftime("%M")
    res = await bot.edit_message_text(f"🟢 🌊 uksivt.xyz\nПоиск по группам, преподам и кабинетам\nвключен {f'{hours}:{mins} {times.day}.{times.month}'}",chat_id=-1002035415883,  message_id=80,reply_markup=keyboard)


async def on_exit(bot: Bot):
    await bot.send_message(chat_id=admins[0], text='выключен')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🐋", url="https://uksivt.xyz/")]])
    tz = pytz.timezone('Asia/Yekaterinburg')
    times = datetime.datetime.now(tz=tz)
    hours = times.strftime("%H")
    mins = times.strftime("%M")
    res = await bot.edit_message_text(f"💤 🌊 uksivt.xyz\nПоиск по группам, преподам и кабинетам\nвыключен {f'{hours}:{mins} {times.day}.{times.month}'}", chat_id=-1002035415883,reply_markup=keyboard, message_id=80)


async def on_check(bot: Bot):
    #await bot.send_message(chat_id=admins[0], text='проверил')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🐋", url="https://uksivt.xyz/")]])
    tz = pytz.timezone('Asia/Yekaterinburg')
    times = datetime.datetime.now(tz=tz)
    hours = times.strftime("%H")
    mins = times.strftime("%M")
    res = await bot.edit_message_text(f"🟢 Последняя проверка {f'{hours}:{mins} {times.day}.{times.month}'}\nuksivt.xyz Поиск по группам, преподам и кабинетам",chat_id=-1002035415883,  message_id=80,reply_markup=keyboard)


async def checkNew(bot: Bot):
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    tables: List[ZamTable] = getAllMonthTables(soup=soup)
    site_links = getAllTablesLinks(tables)
    databaseLinks = GetZamenaFileLinks()
    await on_check(bot=bot)
    if (site_links.__eq__(databaseLinks)):
        pass
    else:
        alreadyFound = await r.lrange("alreadyFound", 0, -1)
        new = list(set(site_links) - set(databaseLinks) - set(alreadyFound))
        new.reverse()
        if (len(new) < 1):
            return
        for link in new:
            print(f'found {link}')
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
                    #await bot.send_media_group(chat_id=admins[0], media=media_group.build())
                    await bot.send_media_group(-1002035415883, media=media_group.build())
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
                parse(link=zamm.link,date=datess,sup=sup)
                await bot.send_message(chat_id=admins[0], text='parsed')
                os.remove(f"{filename}.docx")
            except Exception as error:
                await bot.send_message(chat_id=admins[0], text=f'{str(error)}\n{str(error.__traceback__)}')


@dp.message(F.text, Command("update"))
async def my_update(messsage: Message):
    if messsage.chat.id in admins:
        await  messsage.reply("Проверяю")
        await checkNew(bot=messsage.bot)
        await messsage.reply("Проверил")


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
            date = datetime.date( int(date.split('-')[0] ), int(date.split('-')[1]), int(date.split('-')[2]) )
            response = sup.table("Holidays").insert({"name": name,'date':str(date)}).execute()
            await  message.answer(f'holiday set {response}')
        except Exception as err:
            await message.answer(str(err))


@dp.message(F.text, Command("remove"))
async def my_handlers(message: Message):
    if message.chat.id in admins:
        try:
            date = message.text.split(' ')[1]
            date = datetime.date( int(date.split('-')[0] ), int(date.split('-')[1]), int(date.split('-')[2]) )
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
            date = datetime.date( int(date.split('-')[0] ), int(date.split('-')[1]), int(date.split('-')[2]) )
            link = message.text.split(' ')[2]
            parse(link=link,date=date,sup=sup)
            await message.answer(f'parsed')
        except Exception as error:
            await message.answer(text=f'{str(error)}\n{traceback.format_exc()}')


@dp.message(F.text, Command("latest"))
async def my_handler(message: Message):
    if message.chat.id in admins:
        html = urlopen(SCHEDULE_URL).read()
        soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
        link, date = getLastZamenaLink(soup=soup)
        await message.answer(link)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(minute='0/15', hour='2-17', day_of_week='mon-sat')
    scheduler.add_job(checkNew, trigger, args=(bot,))
    scheduler.start()
    try:
        await on_on(bot=bot)
        await checkNew(bot=bot)
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await on_exit(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
