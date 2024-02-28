import asyncio
import logging
import sys
from typing import List
from urllib.request import urlopen
import time

from aiogram.fsm.storage import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Filter, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from bs4 import BeautifulSoup
from downloader import getLastZamenaLink, SCHEDULE_URL, getAllMonthTables, getAllTablesLinks
from supbase import initSupabase, getCabinets, GetZamenaFileLinks

TOKEN = "5261332325:AAFNow9E-uVnMwsAHvkGbaUdlT0i1wCMRCA"
sup = initSupabase()
dp = Dispatcher()
router = Router()
admins = [1283168392]
r = redis.Redis(host='viaduct.proxy.rlwy.net', port=55121, decode_responses=True,
                    password="1jlO4idEkKK3MKJfL4eIoPmja6ak1FGN", username="default")


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
        if (len(new) < 1):
            return
        for link in new:
            await r.lpush("alreadyFound", str(link))
            # text += (f' \n <a href="{link}">Неизвестная дата</a>')
            text += (f' \n {link}')
        subs = await r.lrange("subs", 0, -1)
        for i in subs:
            await bot.send_message(chat_id=i, text=f"Новые замены \n {text}", parse_mode="HTML")


@dp.message(F.text, Command("update"))
async def my_update(bot: Bot):
    await checkNew(bot=bot)

# @dp.message(F.text, Command("check"))
# async def my_handler(message: Message):
#     html = urlopen(SCHEDULE_URL).read()
#     soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
#     siteLinks = getAllTablesLinks(getAllMonthTables(soup=soup))
#     databaseLinks = GetZamenaFileLinks()
#     if (siteLinks.__eq__(databaseLinks)):
#         await message.answer("Нет новых")
#     else:
#         text = ""
#         for link in list(set(siteLinks) - set(databaseLinks)):
#             # text += (f' \n <a href="{link}">Неизвестная дата</a>')
#             text += (f' \n {link}')
#
#         await message.answer(f"Новые замены \n {text}", parse_mode="HTML")


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




@dp.message(F.text, Command("latest"))
async def my_handler(message: Message):
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    await message.answer(getLastZamenaLink(soup=soup))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    await message.answer(getLastZamenaLink(soup=soup))


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(checkNew, "interval", minutes=30, args=(bot,))
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
