from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Command
from oauth2client.service_account import ServiceAccountCredentials
import os
import gspread
from modules import key
from datetime import datetime, date


users = key.db_get_user_login()

LAST_PROCESSED_ROW_FILE = "last_row.txt"


def get_last_processed_row():
    if os.path.exists(LAST_PROCESSED_ROW_FILE):
        with open(LAST_PROCESSED_ROW_FILE, "r") as file:
            return int(file.read())
    return 1  # Если файл не существует, начни с первой строки


def update_last_processed_row(row):
    with open(LAST_PROCESSED_ROW_FILE, "w") as file:
        file.write(str(row))


credentials_path = os.path.abspath("yoballi-b0a1ba0fa33e.json")

# Инициализация бота и диспетчера
bot = Bot(token='6285611257:AAGcsm_qWuJKPJsWlpdTX9kGiyKKDOU5DS4')
dp = Dispatcher(bot)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(os.path.abspath("yoballi-b0a1ba0fa33e.json"), scope)
client = gspread.authorize(credentials)

spreadsheet_id = '1YppxX9KAuvq0a1tce3jrvjRSdYiBDsPA9V5b7DDz9RA'

worksheet_id = 0
worksheet1 = client.open_by_key(spreadsheet_id).get_worksheet(1)
need_worksheet = 2

cell_coordinates = "B1"  # Например, ячейка B1

gc = gspread.service_account(filename=credentials_path)
table = gc.open_by_key('1YppxX9KAuvq0a1tce3jrvjRSdYiBDsPA9V5b7DDz9RA')
worksheet_history = table.worksheet('История')


def get_current_balance(user):
    list_accurate = worksheet_history.get_all_values()
    summ_of_accurates = 0
    summ_of_write_downs = 0
    for item in list_accurate:
        if item[0] == user:
            if item[2] == "":
                summ_of_accurates += float(item[1])
            elif item[1] == "":
                summ_of_write_downs += float(item[2])
    current_balance = summ_of_accurates - summ_of_write_downs
    return current_balance


async def yoball_info_handler(message: types.Message, state:FSMContext):
    # Открываем таблицу и лист
    async with state.proxy() as data:
        authtorizer_user_find = data.get('login')
        authorized_user = data.get('authorized_user')
        users_new = key.db_get_user_login()
        if authorized_user and authtorizer_user_find in users_new:

            current_balance = get_current_balance(authtorizer_user_find)
            response = (f"Привет {authtorizer_user_find}, твой текущий баланс {current_balance}\n"
                        f"Вот твоя история списаний и начислений:\n")
            list_accurates = worksheet_history.get_all_values()
            message_parts = []
            for item in list_accurates:
                if item[0] == authtorizer_user_find:
                    if item[2] == "":
                        message_text = (f"Начисление: {item[1]}\n"
                                   f"Когда: {item[3]}\n"
                                   f"За что: {item[5]}\n\n")
                    elif item[1] == "":
                        message_text = (f"Списание: {item[2]}\n"
                                   f"Когда: {item[3]}\n"
                                   f"За что: {item[5]}\n\n")
                    message_parts.append(message_text)

            # Максимальная длина сообщения для Telegram
            max_message_length = 4096

            # Отправляем части сообщения
            for part in message_parts:
                if len(response) + len(part) > max_message_length:
                    # Если добавление этой части сделает сообщение слишком длинным, отправляем текущее сообщение
                    await message.answer(response)
                    response = (f"Привет {authtorizer_user_find}, твой текущий баланс {current_balance}\n"
                                f"Продолжение истории списаний и начислений:\n")

                response += part

            await message.answer(response)
        else:
            await message.reply('Ты не авторизован. Введи свой логин и пароль с помощью команды /auth')


async def yoball_admin_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        authtorizer_user_find_2 = data['auth']
        if authtorizer_user_find_2 in key.db_get_user_login() and authtorizer_user_find_2 in key.db_get_admin_login():
            user_actions_keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Начислить ёбаллы"),
                        KeyboardButton(text="Списать ёбаллы"),
                    ],
                    [KeyboardButton(text="Отмена")],
                ],
                resize_keyboard=True,
            )
            await message.reply("Выбери действие:", reply_markup=user_actions_keyboard)
            await state.set_state("accurate_yoballs")
        else:
            await message.reply('Эта команда только для админа')


async def yoball_action_handler(message: types.Message, state: FSMContext):
    action = message.text
    if action == "Начислить ёбаллы":
        await message.reply("Введи логин пользователя, которому хочешь начислить ёбы:")
        await state.set_state("accurate")
    elif action == "Списать ёбаллы":
        await message.reply("Введи логин пользователя, у которого хочешь списать ёбы:")
        await state.set_state("write_down_yoballs")
    elif action == "Отмена":
        await message.reply("Команда отменена.")
        await state.reset_state(with_data=False)
    else:
        await message.reply(
            "Некорректный ввод. Пожалуйста, выбери действие:\n1. Начислить ёбаллы\n2. Списать ёбаллы\n3. Отмена")


async def accurate_yoballs_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Отмена":
            await state.reset_state(with_data=False)
            await message.reply("Команда отменена.")
        else:
            username = message.text
            data['user_name'] = username
            await message.reply("Введи сумму ёбаллов которую хочешь начислить: ")
            await state.set_state("summ_of_acurate")


async def summ_of_acurate_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Отмена":
            await state.reset_state(with_data=False)
            await message.reply("Команда отменена.")
        else:
            accurate = message.text
            today = date.today()
            timestamp = today.strftime("%m/%d/%Y")
            data['timestamp'] = timestamp
            data['accu_rate'] = accurate
            data['time_stamp'] = timestamp
            whom = data['auth']
            data['whom'] = whom
            await message.reply("Теперь напиши за что ты хочешь начислить ёбы: ")
            await state.set_state("for_what")


async def for_what_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Отмена":
            await state.reset_state(with_data=False)
            await message.reply("Команда отменена.")
        else:
            for_what = message.text
            user = data.get('user_name')
            accurate = data.get('accu_rate')
            timestamp = data.get('time_stamp')
            whom = data.get('whom')
            last_processed_row = get_last_processed_row()
            worksheet1.update(f"A{last_processed_row}", f"{user}")
            worksheet1.update(f"B{last_processed_row}", float(accurate))
            worksheet1.update(f"D{last_processed_row}", f"{timestamp}")
            worksheet1.update(f"E{last_processed_row}", f"{whom}")
            worksheet1.update(f"F{last_processed_row}", f"{for_what}")
            last_processed_row += 1
            update_last_processed_row(last_processed_row)
            await state.reset_state(with_data=False)
            await message.reply("Ёбы успешно внесены!")


async def write_downs_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Отмена":
            await state.reset_state(with_data=False)
            await message.reply("Команда отменена.")
        else:
            username = message.text
            data['user_name'] = username
            await message.reply("Введи сумму ёбаллов которую хочешь списать: ")
            await state.set_state("summ_of_write_down")


async def summ_of_write_downs_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Отмена":
            await state.reset_state(with_data=False)
            await message.reply("Команда отменена.")
        else:
            write_down = message.text
            today = date.today()
            timestamp = today.strftime("%d/%m/%Y")
            data['write_down'] = write_down
            data['time_stamp'] = timestamp
            whom = data['auth']
            data['whom'] = whom
            await message.reply("Теперь напиши за что ты хочешь списать ёбы: ")
            await state.set_state("for_what_write_down")


async def for_what_write_down_handler(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Отмена":
            await state.reset_state(with_data=False)
            await message.reply("Команда отменена.")
        else:
            for_what = message.text
            user = data.get('user_name')
            write_down = data.get('write_down')
            timestamp = data.get('time_stamp')
            whom = data.get('whom')
            last_processed_row = get_last_processed_row()
            worksheet1.update(f"A{last_processed_row}", f"{user}")
            worksheet1.update(f"C{last_processed_row}", float(write_down))
            worksheet1.update(f"D{last_processed_row}", f"{timestamp}")
            worksheet1.update(f"E{last_processed_row}", f"{whom}")
            worksheet1.update(f"F{last_processed_row}", f"{for_what}")
            last_processed_row += 1
            update_last_processed_row(last_processed_row)
            await state.reset_state(with_data=False)
            await message.reply("Ёбы успешно списаны!")


def register_handlers_yoball(dp: Dispatcher):
    dp.register_message_handler(yoball_info_handler, Command('yoballs'))
    dp.register_message_handler(yoball_admin_handler, Command('admin_yoballs'))
    dp.register_message_handler(yoball_action_handler, state="accurate_yoballs")
    dp.register_message_handler(accurate_yoballs_handler, state="accurate")
    dp.register_message_handler(summ_of_acurate_handler, state="summ_of_acurate")
    dp.register_message_handler(for_what_handler, state="for_what")
    dp.register_message_handler(write_downs_handler, state="write_down_yoballs")
    dp.register_message_handler(summ_of_write_downs_handler, state="summ_of_write_down")
    dp.register_message_handler(for_what_write_down_handler, state="for_what_write_down")
