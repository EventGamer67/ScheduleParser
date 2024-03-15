import asyncio
import logging
import os
import sys
from typing import List
from urllib.request import urlopen
import time
import datetime
from aiogram.client import bot
from aiogram.fsm.storage import redis
from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Filter, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from bs4 import BeautifulSoup
from downloader import getLastZamenaLink, SCHEDULE_URL, getAllMonthTables, getAllTablesLinks, create_pdf_screenshots, \
    cleanup_temp_files, downloadFile
from supbase import initSupabase, getCabinets, GetZamenaFileLinks, parse
from aiogram.types import FSInputFile

TOKEN = "5261332325:AAEVl8ACJvWB4Pajhm3HHKkklPjCjoVQr_o"
sup = initSupabase()
dp = Dispatcher()
router = Router()
admins = [1283168392]
r = redis.Redis(host='monorail.proxy.rlwy.net', port=13877, decode_responses=True,
                    password="BNFODHMBEaF3fdNd4akOD2CPg5HgEMla", username="default")


async def checkNew(bot: Bot):
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    siteLinks = getAllTablesLinks(getAllMonthTables(soup=soup))
    databaseLinks = GetZamenaFileLinks()
    if (siteLinks.__eq__(databaseLinks)):
        pass
        # subs = await r.lrange("subs", 0, -1)
        # for i in subs:
        #     await bot.send_message(chat_id=i, text="Нет новых")
    else:
        text = ""
        alreadyFound = await r.lrange("alreadyFound", 0, -1)
        new = list(set(siteLinks) - set(databaseLinks) - set(alreadyFound))
        files = []
        if (len(new) < 1):
            return
        for link in new:
            try:
                await r.lpush("alreadyFound", str(link))
                filename = link.split('/')[-1].split('.')[0]
                downloadFile(link=link, filename=f"{filename}.pdf")
                screenshot_paths = await create_pdf_screenshots(filename)
                media_group = MediaGroupBuilder(caption=f"Новые замены \n {link}")
                for i in screenshot_paths:
                    image = FSInputFile(i)
                    media_group.add_photo(image)
                try:
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
            except Exception as error:
                await bot.send_message(chat_id=admins[0], text=str(error))


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
            await  message.answer(f'deleted {deleted[0:10]}')
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
            await  message.answer(f'parsed')
        except Exception as err:
            await message.answer(str(err))


@dp.message(F.text, Command("latest"))
async def my_handler(message: Message):
    if message.chat.id in admins:
        html = urlopen(SCHEDULE_URL).read()
        soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
        await message.answer(getLastZamenaLink(soup=soup))


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(hour='8-20', day_of_week='mon-fri')
    scheduler.add_job(checkNew, trigger, args=(bot,))
    scheduler.start()
    await dp.start_polling(bot)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
