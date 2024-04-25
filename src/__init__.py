import asyncio
from aiogram.fsm.storage import redis
from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import FSInputFile

from src.code.network.supbase import *
from src.code.core.downloader import *
from docx2pdf import convert
from src.code.tools.functions import *

from bs4 import BeautifulSoup
import logging
import os
import sys
import traceback
from typing import List
import pytz
import datetime

# from urllib.request import urlopen
# from aiogram import Bot, Dispatcher, Router, F
# # from code.models.zamena_table_model import ZamTable
# # from code.downloader import getLastZamenaLink, SCHEDULE_URL, getAllMonthTables, getAllTablesLinks, create_pdf_screenshots, cleanup_temp_files, downloadFile
# # from code.functions import get_file_extension
# # from code.supbase import initSupabase, GetZamenaFileLinks, parse


# from docx2pdf import convert
# import hashlib
# from code import *
# from code import *
