import asyncio
import logging
import sys
from urllib.request import urlopen
import time

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
alreadyFound = []

subs = []



async def checkNew(bot: Bot):
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    siteLinks = getAllTablesLinks(getAllMonthTables(soup=soup))
    databaseLinks = GetZamenaFileLinks()
    if (siteLinks.__eq__(databaseLinks)):
        for i in subs:
            await bot.send_message(chat_id=i,text="Нет новых")
    else:
        text = ""
        new = list(set(siteLinks) - set(databaseLinks) - set(alreadyFound))
        if(len(new) < 1):
            return
        for link in new:
            alreadyFound.append(link)
            # text += (f' \n <a href="{link}">Неизвестная дата</a>')
            text += (f' \n {link}')
        for i in subs:
            await bot.send_message(chat_id=i, text=f"Новые замены \n {text}", parse_mode="HTML")


@dp.message(F.text, Command("check"))
async def my_handler(message: Message):
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    siteLinks = getAllTablesLinks(getAllMonthTables(soup=soup))
    databaseLinks = GetZamenaFileLinks()
    if(siteLinks.__eq__(databaseLinks)):
        await message.answer("Нет новых")
    else:
        text = ""
        for link in list(set(siteLinks) - set(databaseLinks)):
            #text += (f' \n <a href="{link}">Неизвестная дата</a>')
            text += (f' \n {link}')

        await message.answer(f"Новые замены \n {text}",parse_mode="HTML")


@dp.message(F.text, Command("sub"))
async def my_handler(message: Message):
    subs.append(message.chat.id)
    await message.answer("Подписан")


@dp.message(F.text, Command("unsub"))
async def my_handler(message: Message):
    subs.remove(message.chat.id)
    await message.answer("Отписан")


@dp.message(F.text, Command("latest"))
async def my_handler(message: Message):
    await message.answer(str(message.chat.id))
    # html = urlopen(SCHEDULE_URL).read()
    # soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    # await message.answer(getLastZamenaLink(soup=soup))


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    html = urlopen(SCHEDULE_URL).read()
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    await message.answer( getLastZamenaLink(soup=soup) )

async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(checkNew, "interval", minutes=2, args=(bot,))
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


