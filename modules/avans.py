from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types
import gspread
from datetime import date
import os

LAST_PROCESSED_ROW_FILE = 'last_row_avans.txt'


def get_last_processed_row():
    if os.path.exists(LAST_PROCESSED_ROW_FILE):
        with open(LAST_PROCESSED_ROW_FILE, "r") as file:
            return int(file.read())
    return 1  # Если файл не существует, начни с первой строки


def update_last_processed_row(row):
    with open(LAST_PROCESSED_ROW_FILE, "w") as file:
        file.write(str(row))


credentials_path = 'avans-401601-8da79f13d95d.json'
gc = gspread.service_account('avans-401601-8da79f13d95d.json')
# table = gc.open_by_key('1D_vaCX4yh6KGz7WR5OVjq5BDGf39fUzITkxkMbQUrmo')
worksheet = "Добавить сюда позже"
# worksheet = table.worksheet('1')


def get_current_row():
    current_list = worksheet.col_values(1)
    current_list.append(' ')
    count = 0
    for item in current_list:
        count += 1
        if item == " ":
            break
    return count


async def avans_start_handler(message: types.Message, state: FSMContext):
    await message.answer("Команда больше недоступна")
    # async with state.proxy() as data:
    #     authorized_user = data.get('authorized_user')
    #     if authorized_user:
    #         options = ['Продолжить', 'Отмена']
    #         markup = ReplyKeyboardMarkup(resize_keyboard=True)
    #         for option in options:
    #             markup.add(KeyboardButton(option))
    #         await message.answer('Привет нажми "Продолжить", что бы внести аванс, или нажми "Отмена",'
    #                              ' что бы отменить действие', reply_markup=markup)
    #         await state.set_state("avans_summ")
    #     else:
    #         await message.reply("Ты не авторизован. Введи свой логин и пароль с помощью команды /auth")


async def avans_summ_handler(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await state.reset_state(with_data=False)
        await message.reply("Команда отменена")
    else:
        await state.set_state("avans_place")
        await message.reply("Введи сумму аванса")


async def avans_place_handler(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await state.reset_state(with_data=False)
        await message.reply("Команда отменена")
    else:
        async with state.proxy() as data:
            avans_summ = message.text
            data['avans_summ'] = avans_summ
            await message.answer("На какой точке взял аванс ? ")
            await state.set_state("register_avans")


async def register_avans_handler(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await state.reset_state(with_data=False)
        await message.reply("Команда отменена")
    else:
        async with state.proxy() as data:
            user = data.get('auth')
            today = date.today()
            timestamp = today.strftime("%d/%m/%Y")
            avans_summ = data.get('avans_summ')
            avans_place = message.text

            row = get_current_row()
            worksheet.update(f"A{row}", user)
            worksheet.update(f'B{row}', timestamp)
            worksheet.update(f'C{row}', avans_summ)
            worksheet.update(f'D{row}', avans_place)

            await state.reset_state(with_data=False)
            await message.reply("Аванс успешно внесён")


def register_handlers_avans(dp: Dispatcher):
    dp.register_message_handler(avans_start_handler, commands='avans', state='*')
    dp.register_message_handler(avans_summ_handler, state='avans_summ')
    dp.register_message_handler(avans_place_handler, state='avans_place')
    dp.register_message_handler(register_avans_handler, state="register_avans")
