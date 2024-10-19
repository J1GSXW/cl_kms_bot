import io
import os
import json
import time
from datetime import datetime
import pytz
from aiogram import Dispatcher
from aiogram import executor
from googleapiclient.discovery import build
from google.oauth2 import service_account
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from google.oauth2.service_account import Credentials
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types
import logging
from create_bot import dp, bot
import sqlite3 as sq
from modules import on_startup

credentials_path = 'key-table-884e22e34671.json'
spreadsheet_id = '1Earajl5uvYB4K-itbZL3RId7tcW_KOh8OhkUFiqUOxk'


class InfoState(StatesGroup):
    SELECT_POINT = State()


class EditState(StatesGroup):
    SELECT_POINT = State()
    SELECT_KEY = State()
    ENTER_NAME = State()


class AuthState(StatesGroup):
    LOGIN = State()
    PASSWORD = State()


def db_add_changes(user, key, data, previous_value, timestamp):
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        sq_insert_with_params = """INSERT INTO changes
                                (user, cell, data, previous_value, timestamp)
                                VALUES (?, ?, ?, ?, ?)"""
        data_turple = (user, key, data, previous_value, timestamp)
        cur.execute(sq_insert_with_params, data_turple)


@dp.message_handler(commands='send_db')
async def send_db(message: types.Message):
    with open('Cof_Like_bot.db', 'rb') as f:
        await message.answer_document(types.InputFile(f, filename='Cof_Like_bot.db'), caption="Вот тебе бд")


def db_see_changes():
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        sq_insert = "SELECT * FROM (SELECT * FROM changes ORDER BY change_id DESC LIMIT 10) ORDER BY change_id ASC;"
        changes = cur.execute(sq_insert)
        return changes


def db_clear_changes():
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        sq_insert = "DELETE FROM changes"
        cur.execute(sq_insert)


def db_add_user(username, password):
    with sq.connect("Cof_Like_bot.db") as con3:
        cur3 = con3.cursor()
        sq_insert_with_param = """INSERT INTO users (login, password) VALUES (?, ?);"""
        data_turple = (username, password)
        cur3.execute(sq_insert_with_param, data_turple)


def db_delete_user(username):
    with sq.connect("Cof_Like_bot.db") as con4:
        cur4 = con4.cursor()
        sq_insert_with_param = """DELETE from users where login = ?"""
        cur4.execute(sq_insert_with_param, (username,))
        cur4.close()


def db_get_user_login():
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        user_login_res = cur.execute("SELECT login, password FROM users")
        user_login_password = user_login_res.fetchall()
        users_list = []
        for users in user_login_password:
            users_list.append(users[0])
        cur.close()
        return users_list


def db_get_admin_login():
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        user_login_res = cur.execute("SELECT login, password FROM admins")
        user_login_password = user_login_res.fetchall()
        users_list = []
        for users in user_login_password:
            users_list.append(users[0])
    return users_list


def db_get_user_login_str(user):
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        user_login_res = cur.execute("SELECT login, password FROM users")
        user_login_password = user_login_res.fetchall()
        for users in user_login_password:
            if users[0] == user:
                cur.close()
                return users[0]

def db_get_user_password_str(user):
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        user_login_res = cur.execute("SELECT login, password FROM users")
        user_login_password = user_login_res.fetchall()
        for users in user_login_password:
            if users[0] == user:
                cur.close()
                return users[1]

def db_get_user_login_str():
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        user_login_res = cur.execute("SELECT login, password FROM users")
        user_login_password = user_login_res.fetchall()
        passwords_list = []
        for passwors in user_login_password:
            passwords_list.append(passwors[1])
    cur.close()
    return passwords_list



def db_get_auth_data(user):
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        user_login_res = cur.execute("SELECT login, password FROM users")
        user_login_password = user_login_res.fetchall()
        login = ""
        password = ""
        user_data = ()
        for users in user_login_password:
            if users[0] == user:
                user_data = users
    cur.close()
    return user_data

def db_get_user_login_turple():
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        user_login_res = cur.execute("SELECT login, password FROM users")
        user_login_password = user_login_res.fetchall()
    cur.close()
    return user_login_password

changes = {}

authtorizer_user_find = None

authtorizer_user_find_2 = None


# @dp.message_handler(commands=['users'], state='*')
async def users_command_handler(message: types.Message, state: FSMContext):
    user_actions_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Добавить пользователя"),
                KeyboardButton(text="Удалить пользователя"),
            ],
            [KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True,
    )
    async with state.proxy() as data:
        authtorizer_user_find_2 = data['auth']
        if authtorizer_user_find_2 in db_get_user_login() and authtorizer_user_find_2 in db_get_admin_login():
            await message.reply("Выбери действие:", reply_markup=user_actions_keyboard)
            await state.set_state("user_action")
        else:
            await message.reply("Эта команда только для админа, друг☹️")


# @dp.message_handler(state="user_action")
async def user_action_handler(message: types.Message, state: FSMContext):
    action = message.text
    if action == "Добавить пользователя":
        await message.reply("Введи логин пользователя:")
        await state.set_state("add_username")
    elif action == "Удалить пользователя":
        await message.reply("Введи логин пользователя для удаления:")
        await state.set_state("delete_username")
    elif action == "Отмена":
        await message.reply("Команда отменена.")
        await state.reset_state(with_data=False)
    else:
        await message.reply(
            "Некорректный ввод. Пожалуйста, выбери действие:\n1. Добавить пользователя\n2. Удалить пользователя\n3. Отмена")


# @dp.message_handler(state="add_username")
async def add_username_handler(message: types.Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.reply("Введи пароль пользователя:")
    await state.set_state("add_password")

# @dp.message_handler(state="add_password")
async def add_password_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = data.get("username")
    password = message.text
    if username and password:
        db_add_user(username, password)

        await message.reply("Пользователь успешно добавлен.")
    else:
        await message.reply("Произошла ошибка. Пользователь не добавлен.")
    await state.reset_state(with_data=False)


# @dp.message_handler(state="delete_username")
async def delete_username_handler(message: types.Message, state: FSMContext):
    username = message.text
    if username in db_get_user_login():
        db_delete_user(username)
        await message.reply("Пользователь успешно удален.")
    else:
        await message.reply("Пользователь не найден.")
    await state.reset_state(with_data=False)


# @dp.message_handler(commands=['see_users'], state='*')
async def see_users_command_handler(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        authtorizer_user_find_2 = data['auth']
        if authtorizer_user_find_2 in db_get_user_login() and authtorizer_user_find_2 in db_get_admin_login():
            users_text = "Список пользователей:\n"
            user_login_password1 = db_get_user_login_turple()
            for username, password in user_login_password1:
                users_text += f"Логин: {username}, Пароль: {password}\n"
            await message.reply(users_text)
        else:
            await message.reply("Эта команда только для админа, друг☹️")

# Функция для обновления ячейки в таблице Google Sheets
def edit_google_sheet(cell, data, user):
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=credentials)
    global authtorizer_user_find
    range_name = f'Лист1!{cell}'
    sheet_values = [[data]]
    try:
        # Получить текущее значение ячейки
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()

        previous_value = result['values'][0][0] if 'values' in result and result['values'] else None

        # Обновить ячейку
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body={'values': sheet_values}
        ).execute()
        if 'updatedCells' in result:
            curent_timezone = pytz.timezone('Asia/Vladivostok')
            current_date = datetime.now(curent_timezone)
            current_date_string = current_date.strftime('%m/%d/%y %H:%M:%S')
            datetime_obj = datetime.strptime(current_date_string, '%m/%d/%y %H:%M:%S')
            timestamp = datetime_obj
            cells = get_key_for_func(cell)
            db_add_changes(user, cells, data, previous_value, timestamp)
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Не удалось обновить таблицу Google: {e}")
        return False


# @dp.message_handler(commands=['admin'], state='*')
async def admin_command_handler(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        authtorizer_user_find_2 = data['auth']
        if authtorizer_user_find_2 in db_get_user_login() and authtorizer_user_find_2 in db_get_admin_login():
            changes_list = db_see_changes()
            if not changes_list:
                await message.reply("Нет внесенных изменений.")
            else:
                response = "Список внесенных изменений:\n"
                for changes in changes_list:
                    user = changes[1]
                    key = changes[2]
                    data = changes[3]
                    timestamp = changes[4]
                    previous_value = changes[5]
                    response += f"Пользователь: {user}\n"
                    response += f"Номер ключика: {key}\n"
                    response += f"Что было в ячейке: {previous_value}\n"
                    response += f"Что стало в ячейке: {data}\n"
                    response += f"Время изменения: {timestamp}\n\n"
                await message.reply(response)
        else:
            await message.reply("У вас нет прав доступа к этой команде.")


# @dp.message_handler(commands=['clear_changes'], state='*')
async def clear_changes_command_handler(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        authtorizer_user_find_2 = data['auth']
        if authtorizer_user_find_2 in db_get_user_login() and authtorizer_user_find_2 in db_get_admin_login():
            db_clear_changes()
            await message.reply("Список изменений был очищен👍.")
        else:
            await message.reply("Эта команда только для админа, друг☹️")


def get_key_for_func(cell):
    cell_mapping = {
        'B4': '1.1',
        'B5': '1.2',
        'B6': '1.3',
        'B7': '1.4',
        'B8': '1.5',
        'B9': '1.6',
        'B10': '1.7',
        'B11': '1.8',
        'D4': '2.1',
        'D5': '2.2',
        'D6': '2.3',
        'D7': '2.4',
        'D8': '2.5',
        'D9': '2.6',
        'F4': '3.1',
        'F5': '3.2',
        'F6': '3.3',
        'F7': '3.4',
        'F8': '3.5',
        'F9': '3.6',
        'F10': '3.7',
        'H4': '5.1',
        'H5': '5.2',
        'H6': '5.3',
        'H7': '5.4',
        'J4': '6.1',
        'J5': '6.2',
        'J7': '6.3',
        'J7': '6.4',
        'J8': '6.5',
        'J9': '6.6',
        'J10': '6.7',
        'J11': '6.8',
        'L4': '7.1',
        'L5': '7.2',
        'L6': '7.3',
        'L7': '7.4',
        'L8': '7.5',
        'L9': '7.6',
        'L10': '7.7',
        'L11': '7.8',
        'N4': '8.1',
        'N5': '8.2',
        'N6': '8.3',
        'N7': '8.4',
        'N8': '8.5',
    }
    key = cell_mapping.get(cell)
    return key


def get_google_sheet_data(cell_ranges):
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
    service = build('sheets', 'v4', credentials=credentials)

    try:
        results = []
        for cell_range in cell_ranges:
            range_name = f'Лист1!{cell_range}'
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_name
            ).execute()
            values = result.get('values', [])
            results.append(values)

        return results
    except Exception as e:
        logging.error(f"Не удалось получить данные из таблицы Google: {e}")
        return None


# @dp.message_handler(commands=['auth'])
async def auth_command_handler(message: types.Message, state: FSMContext):
    user_id = message.from_id
    on_startup.save_user_id(user_id)
    async with state.proxy() as data:
        authorized_user = data.get('authorized_user')
        if authorized_user:
            await message.reply("Ты уже авторизован, друг, можешь пользоваться ботом!👍")
        else:
            await AuthState.LOGIN.set()
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add("Отмена")

            await message.reply("Введи свой логин:", reply_markup=keyboard)


# @dp.message_handler(state=AuthState.LOGIN)
async def login_handler(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.answer("Команда отменена")
        await state.reset_state(with_data=False)
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add("Отмена")
        global authtorizer_user_find
        login = message.text.strip()
        if login in db_get_user_login():
            async with state.proxy() as data:
                # Сохраняем логин пользователя
                data['login'] = login
                data['auth'] = login
                authtorizer_user_find = data['login']
            await AuthState.PASSWORD.set()

            await message.reply("Введи свой пароль:", reply_markup=keyboard)
        else:
            await message.reply("Неверный логин. Попробуй снова.", reply_markup=keyboard)


# @dp.message_handler(state=AuthState.PASSWORD)
async def password_handler(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.answer("Команда отменена")
        await state.reset_state(with_data=False)
    else:
        password = message.text.strip()
        async with state.proxy() as data:
            login = data.get('login')  # Получаем сохраненный логин пользователя
            user_data = str(db_get_user_password_str(login))
            if login and password == user_data:
                # Пользователь успешно авторизован, сохраняем его идентификатор
                data['authorized_user'] = login
                await state.finish()
                await message.reply(f"Ты успешно авторизован как {login}!")
            else:
                await message.reply("Неверный пароль. Попробуй снова, друг.")


# @dp.message_handler(commands='start')
async def start_handler(message: types.Message):
    user_id = message.from_id
    on_startup.save_user_id(user_id)
    await message.answer("Привет, ты попал в бота CL_KMS, вот список доступных команд\n"
                         "/auth - ввести логин и пароль\n"
                         "/training - тренажёр ТТК\n"
                         "/yoballs - посмотреть баланс Ёбаллов\n")


# @dp.message_handler(commands=['start'])
async def key_command_handler(message: types.Message, state: FSMContext):
    await message.answer("Команда больше недоступна")
    # async with state.proxy() as data:
    #     authorized_user = data.get('authorized_user')
    #     if authorized_user:
    #         await state.update_data(authorized_user=authorized_user)
    #         options = ['Взять/отдать ключи', 'Показать актуальную информацию о ключах']
    #         markup = ReplyKeyboardMarkup(resize_keyboard=True)
    #         for option in options:
    #             markup.add(KeyboardButton(option))
    #         await message.reply("Привет! Что бы ты хотел сделать?", reply_markup=markup)
    #     else:
    #         await message.reply("Ты не авторизован. Введи свой логин и пароль с помощью команды /auth")


# @dp.message_handler(Text(equals='Показать актуальную информацию о ключах'), state= '*')
async def show_keys_info_handler(message: types.Message, state: FSMContext):
    await message.answer("Опция больше недоступна")
#     async with state.proxy() as data:
#         authtorizer_user_find = data['login']
#         authorized_user = data.get('authorized_user')
#         if authorized_user and authtorizer_user_find in db_get_user_login():
#             options = ['Ленина 1.1 - 1.8', 'Драм 2.1 - 2.6', 'Факел 3.1 - 3.7', 'Карусель 5.1 - 5.4',
#                        'Дикопольцева 6.1 - 6.8', 'Аврора 7.1 - 7.8', 'Кирова 8.1 - 8.5']
#             markup = InlineKeyboardMarkup(row_width=2)
#             for option in options:
#                 callback_data = f'show_info_{option}'
#                 markup.add(InlineKeyboardButton(option, callback_data=callback_data))
#             await message.reply("Выбери точку, ключи от которой тебя интересуют:", reply_markup=markup)
#         else:
#             await message.reply("Ты не авторизован. Введи свой логин и пароль с помощью команды /auth")


# @dp.callback_query_handler(lambda query: query.data.startswith('show_info_'), state='*')
async def handle_show_info_callback(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        authtorizer_user_find = data['login']
        authorized_user = data.get('authorized_user')
        if authorized_user and authtorizer_user_find in db_get_user_login():
            option = query.data.replace('show_info_', '').split(' ', 1)[0]
            cell_ranges = get_cell_ranges(option)
            data = get_google_sheet_data(cell_ranges)
            if data:
                response = f"Вот тебе информация о ключах от {option}:\n"
                for values in data:
                    for row in values:
                        response += ", ".join(row) + "\n"
                await query.message.reply(response)
            else:
                await query.message.reply(
                    "Не удалось получить данные из таблицы. Пожалуйста, попробуй снова, или напиши ИА о проблеме.")
            await query.answer()
        else:
            await query.message.reply('Ты не авторизован. Введи свой логин и пароль с помощью команды /auth')


def get_cell_ranges(option):
    if option == 'Ленина':
        return ['A4:B11']
    elif option == 'Факел':
        return ['E4:F10']
    elif option == 'Дикопольцева':
        return ['I4:J11']
    elif option == 'Карусель':
        return ['G4:H7']
    elif option == 'Аврора':
        return ['K4:L11']
    elif option == 'Драм':
        return ['C4:D9']
    elif option == 'Кирова':
        return ['M4:N8']

    else:
        return []


# @dp.message_handler(Text(equals='Взять/отдать ключи'), state='*')
async def manage_keys_handler(message: types.Message, state: FSMContext):
    await message.answer("Опция больше недоступна")
#     async with state.proxy() as data:
#         authtorizer_user_find = data['login']
#         authorized_user = data.get('authorized_user')
#         if authorized_user and authtorizer_user_find in db_get_user_login():
#             options = ['Ленина 1.1 - 1.8', 'Драм 2.1 - 2.6', 'Факел 3.1 - 3.7', 'Карусель 5.1 - 5.4',
#                        'Дикопольцева 6.1 - 6.8', 'Аврора 7.1 - 7.8', 'Кирова 8.1 - 8.5']
#             markup = InlineKeyboardMarkup(row_width=2)
#             for option in options:
#                 callback_data = f'select_point_{option}'
#                 markup.add(InlineKeyboardButton(option, callback_data=callback_data))
#             await message.reply("Выбери точку, ключики от которой хочешь взять/отдать:", reply_markup=markup)
#         else:
#             await message.reply("Ты не авторизован. Введи свой логин и пароль с помощью команды /auth")


# @dp.callback_query_handler(lambda query: query.data.startswith('select_point_'), state='*')
async def handle_select_point_callback(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        authtorizer_user_find = data['login']
        authorized_user = data.get('authorized_user')
        if authorized_user and authtorizer_user_find in db_get_user_login():
            data = query.data.replace('select_point_', '')
            option = data.split(' ', 1)[0]
            keys = get_keys_for_option(option)
            buttons = []
            for key in keys:
                buttons.append(InlineKeyboardButton(key, callback_data=f'select_key_{option}_{key}'))
            buttons.append(InlineKeyboardButton("Назад", callback_data="back"))
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)
            await query.message.reply("Выбери ключик:", reply_markup=keyboard)
            await EditState.SELECT_KEY.set()
            await query.answer()
        else:
            await query.message.reply('Ты не авторизован. Введи свой логин и пароль с помощью команды /auth')

        # @dp.callback_query_handler(lambda query: query.data.startswith('select_key_'), state=EditState.SELECT_KEY)


async def handle_select_key_callback(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        authtorizer_user_find = data['login']
        authorized_user = data.get('authorized_user')
        if authorized_user and authtorizer_user_find in db_get_user_login():
            data = query.data.replace('select_key_', '')
            option, key = data.split('_')
            async with state.proxy() as data:
                data['selected_key'] = key

            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(InlineKeyboardButton("Назад", callback_data="back"))

            await query.message.reply(f"Напиши где теперь ключи {key}:", reply_markup=keyboard)
            await EditState.ENTER_NAME.set()
            await state.update_data(previous_handler="select_key")
            await query.answer()
        else:
            await query.message.reply('Ты не авторизован. Введи свой логин и пароль с помощью команды /auth')

        # @dp.message_handler(state=EditState.ENTER_NAME)


async def handle_enter_name(message: types.Message, state: FSMContext):
    name = message.text
    async with state.proxy() as data:
        authtorizer_user_find = data['login']
        authorized_user = data.get('authorized_user')
        if authorized_user and authtorizer_user_find in db_get_user_login():
            key = data['selected_key']
            option = key.split('.')[0]
            authtorizer_user_find = data['login']
            cell = get_cell_for_key(option, str(key))
            if edit_google_sheet(cell, name, authtorizer_user_find):
                await message.reply("Таблица успешно обновлена👍.")
            else:
                await message.reply(
                    "Не удалось обновить данные. Пожалуйста, попробуй снова или напишите ИА о проблеме.")
            await state.reset_state(with_data=False)
            return
        else:
            await message.reply('Ты не авторизован. Введи свой логин и пароль с помощью команды /auth')


# @dp.callback_query_handler(lambda query: query.data == 'back', state=EditState.SELECT_KEY)
async def handle_back_button_from_select_key(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        authorized_user = data.get('authorized_user')
    await manage_keys_handler(query.message, state)
    async with state.proxy() as data:
        data['authorized_user'] = authorized_user
    await query.answer()


# @dp.callback_query_handler(lambda query: query.data == 'back', state=EditState.ENTER_NAME)
async def handle_back_button_from_enter_name(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        authorized_user = data.get('authorized_user')
    await manage_keys_handler(query.message, state)
    async with state.proxy() as data:
        data['authorized_user'] = authorized_user
    await state.update_data(previous_handler="back")
    await query.answer()


def get_keys_for_option(option):
    keys = []
    if option == 'Ленина':
        keys = [f'1.{i}' for i in range(1, 9)]
    elif option == 'Драм':
        keys = [f'2.{i}' for i in range(1, 7)]
    elif option == 'Факел':
        keys = [f'3.{i}' for i in range(1, 8)]
    elif option == 'Карусель':
        keys = [f'5.{i}' for i in range(1, 5)]
    elif option == 'Дикопольцева':
        keys = [f'6.{i}' for i in range(1, 9)]
    elif option == 'Аврора':
        keys = [f'7.{i}' for i in range(1, 9)]
    elif option == 'Кирова':
        keys = [f'8.{i}' for i in range(1, 6)]
    return keys


def get_cell_for_key(option, key):
    cell_mapping = {
        ('1', '1.1'): 'B4',
        ('1', '1.2'): 'B5',
        ('1', '1.3'): 'B6',
        ('1', '1.4'): 'B7',
        ('1', '1.5'): 'B8',
        ('1', '1.6'): 'B9',
        ('1', '1.7'): 'B10',
        ('1', '1.8'): 'B11',
        ('2', '2.1'): 'D4',
        ('2', '2.2'): 'D5',
        ('2', '2.3'): 'D6',
        ('2', '2.4'): 'D7',
        ('2', '2.5'): 'D8',
        ('2', '2.6'): 'D9',
        ('3', '3.1'): 'F4',
        ('3', '3.2'): 'F5',
        ('3', '3.3'): 'F6',
        ('3', '3.4'): 'F7',
        ('3', '3.5'): 'F8',
        ('3', '3.6'): 'F9',
        ('3', '3.7'): 'F10',
        ('5', '5.1'): 'H4',
        ('5', '5.2'): 'H5',
        ('5', '5.3'): 'H6',
        ('5', '5.4'): 'H7',
        ('6', '6.1'): 'J4',
        ('6', '6.2'): 'J5',
        ('6', '6.3'): 'J6',
        ('6', '6.4'): 'J7',
        ('6', '6.5'): 'J8',
        ('6', '6.6'): 'J9',
        ('6', '6.7'): 'J10',
        ('6', '6.8'): 'J11',
        ('7', '7.1'): 'L4',
        ('7', '7.2'): 'L5',
        ('7', '7.3'): 'L6',
        ('7', '7.4'): 'L7',
        ('7', '7.5'): 'L8',
        ('7', '7.6'): 'L9',
        ('7', '7.7'): 'L10',
        ('7', '7.8'): 'L11',
        ('8', '8.1'): 'N4',
        ('8', '8.2'): 'N5',
        ('8', '8.3'): 'N6',
        ('8', '8.4'): 'N7',
        ('8', '8.5'): 'N8',
    }
    cell = cell_mapping.get((option.lower(), key.lower()), '')
    return cell


def register_handlers_key(dp: Dispatcher):
    dp.register_message_handler(users_command_handler, commands=['users'], state='*')
    dp.register_message_handler(user_action_handler, state="user_action")
    dp.register_message_handler(add_username_handler, state="add_username")
    dp.register_message_handler(add_password_handler, state="add_password")
    dp.register_message_handler(delete_username_handler, state="delete_username")
    dp.register_message_handler(see_users_command_handler, commands=['see_users'], state='*')
    dp.register_message_handler(admin_command_handler, commands=['admin'], state='*')
    dp.register_message_handler(clear_changes_command_handler, commands=['clear_changes'], state='*')
    dp.register_message_handler(auth_command_handler, commands=['auth'])
    dp.register_message_handler(login_handler, state=AuthState.LOGIN)
    dp.register_message_handler(password_handler, state=AuthState.PASSWORD)
    dp.register_message_handler(key_command_handler, commands=['key'])
    dp.register_message_handler(start_handler, commands='start')
    dp.register_message_handler(show_keys_info_handler, Text(equals='Показать актуальную информацию о ключах'),
                                state='*')
    dp.register_callback_query_handler(handle_show_info_callback, lambda query: query.data.startswith('show_info_'),
                                       state='*')
    dp.register_message_handler(manage_keys_handler, Text(equals='Взять/отдать ключи'), state='*')
    dp.register_callback_query_handler(handle_select_point_callback,
                                       lambda query: query.data.startswith('select_point_'), state='*')
    dp.register_callback_query_handler(handle_select_key_callback, lambda query: query.data.startswith('select_key_'),
                                       state=EditState.SELECT_KEY)
    dp.register_message_handler(handle_enter_name, state=EditState.ENTER_NAME)
    dp.register_callback_query_handler(handle_back_button_from_select_key, lambda query: query.data == 'back',
                                       state=EditState.SELECT_KEY)
    dp.register_callback_query_handler(handle_back_button_from_enter_name, lambda query: query.data == 'back',
                                       state=EditState.ENTER_NAME)
