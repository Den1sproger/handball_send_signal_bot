import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

TOKEN = os.getenv('HANDBALL_SEND_TOKEN')
ADMIN = int(os.getenv('ADMIN'))
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())