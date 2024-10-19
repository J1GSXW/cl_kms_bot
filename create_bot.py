from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot_token = '6221924149:AAHJ1MIefk-5Bes22xRJmxZrCpKiJcPh7Lc'

bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
