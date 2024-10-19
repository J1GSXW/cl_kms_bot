from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import types
from create_bot import bot
import gspread
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

credentials_path = 'avans-401601-8da79f13d95d.json'
gc = gspread.service_account(credentials_path)

table_lenina = gc.open_by_key('1mf4jhx0DST519CeVMQMSIJN6Gl-91EWKsEkAEOWrUwA')
worksheet_lenina = table_lenina.worksheet('Ленина')
worksheet_lenina_names = table_lenina.worksheet('Справочник')

table_aurora = gc.open_by_key('1FOzkljof0flfr7uKWneQDJqVZA1-5AqL_vB9W5FfKeA')
worksheet_aurora = table_aurora.worksheet('Аврора')
worksheet_aurora_names = table_aurora.worksheet('Справочник')

table_kirova = gc.open_by_key('1ig-LWE-wfwCCoMffcc75imwbtmuiUYFFiL4wxl5slbM')
worksheet_kirova = table_kirova.worksheet('Кирова')
worksheet_kirova_names = table_kirova.worksheet('Справочник')

table_onix = gc.open_by_key('1n7hGmXF0ApIX7jnn9bkpNn0PFN_uHxo-TqJmzSJCY1Y')
worksheet_onix = table_onix.worksheet('Омникс')
worksheet_onix_names = table_onix.worksheet('Справочник')

table_beeline = gc.open_by_key('1CSNlsU_7LLq-5M_-rAIy0xBL4IM-DOw1fkdAF8pC3jo')
worksheet_beeline = table_beeline.worksheet('Билайн')
worksheet_beeline_names = table_beeline.worksheet('Справочник')

table_fakel = gc.open_by_key('1L5WjQ4-CdqK2JMBMgmmx67-XEbTHXiOqzgXUv3nTnQk')
worksheet_fakel = table_fakel.worksheet('Факел')
worksheet_fakel_names = table_fakel.worksheet('Справочник')

table_karousel = gc.open_by_key('1nQxu7LZMWIjumblm20UZgYRO9zedArZtQBitMhVYsH4')
worksheet_karousel = table_karousel.worksheet('Карусель')
worksheet_karousel_names = table_karousel.worksheet('Справочник')

table_samberi = gc.open_by_key('1MlXO07X3Sdugv8kqmwSEzOI9sAna2Qv-eTrfmB8abDE')
worksheet_samberi = table_samberi.worksheet('Самбос')
worksheet_samberi_names = table_samberi.worksheet('Справочник')

table_rainbow = gc.open_by_key('1Zu6xTviGhG0szsnlYPPbPKt_Mz8u611Cd2roPeLFHuo')
worksheet_rainbow = table_rainbow.worksheet('Радуга')
worksheet_rainbow_names = table_rainbow.worksheet('Справочник')

table_dickopolceva = gc.open_by_key('1vJcmbYjjhiCdLN0uxW1nddX-PSWTqTU3cJmjcPa7QME')
worksheet_dickopolceva = table_dickopolceva.worksheet('Дископольцева')
worksheet_dickopolceva_names = table_dickopolceva.worksheet('Справочник')

table_dramtheatre = gc.open_by_key('1_v5jSKq7507oucSm70sTdMGZYr6nGKjDaF5ZKgKS_OU')
worksheet_dramtheatre = table_dramtheatre.worksheet('Драмтеатр')
worksheet_dramtheatre_names = table_dramtheatre.worksheet('Справочник')

worksheets = {'Ленина': worksheet_lenina,
              'Аврора': worksheet_aurora,
              'Кирова': worksheet_kirova,
              'Оникс': worksheet_onix,
              'Билайн': worksheet_beeline,
              'Факел': worksheet_fakel,
              'Карусель': worksheet_karousel,
              'Самбери': worksheet_samberi,
              'Радуга': worksheet_rainbow,
              'Дикопольцева': worksheet_dickopolceva,
              'Драмтеатр': worksheet_dramtheatre}

worksheet_names = {'Ленина': worksheet_lenina_names,
                   'Аврора': worksheet_aurora_names,
                   'Кирова': worksheet_kirova_names,
                   'Оникс': worksheet_onix_names,
                   'Билайн': worksheet_beeline_names,
                   'Факел': worksheet_fakel_names,
                   'Карусель': worksheet_karousel_names,
                   'Самбери': worksheet_samberi_names,
                   'Радуга': worksheet_rainbow_names,
                   'Дикопольцева': worksheet_dickopolceva_names,
                   'Драмтеатр': worksheet_dramtheatre_names}

full_day = ['Кирова', 'Оникс', 'Билайн', 'Карусель', 'Самбери', 'Радуга', 'Дикопольцева', 'Драмтеатр']
not_full_day = ['Ленина', 'Аврора', 'Факел']


async def get_inline_keyboard(state: FSMContext):
    today = datetime.now()
    date_format = "%d.%m.%y"
    keyboard = InlineKeyboardMarkup(row_width=3)

    # Создайте 8 кнопок с предыдущими датами
    for i in range(8, 0, -1):
        prev_date = today - timedelta(days=i)
        button_text = prev_date.strftime(date_format)
        keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=f"date_{button_text}"))

    # Создайте кнопку с текущей датой в конце
    current_date = today.strftime(date_format)
    keyboard.insert(InlineKeyboardButton(text=current_date, callback_data=f"date_{current_date}"))

    # Создайте кнопку "Назад" с командой для смены состояния
    back_button = InlineKeyboardButton("Назад", callback_data="back_to_start")
    cancel_button = InlineKeyboardButton('Отмена', callback_data='cancel_calendar')
    keyboard.insert(back_button)
    keyboard.insert(cancel_button)

    return keyboard


# @dp.message_handler(text="cancel_calendar", state="*")
async def cancel_calendar(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Команда отменена, воспользуйся ей ещё раз,"
                                                        " что бы начать сначала")
    await state.reset_state(with_data=False)


# @dp.callback_query_handler(text='back_to_start', state='*')
async def go_back_to_start(callback_query: types.CallbackQuery, state: FSMContext):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for keys in worksheets:
        markup.add(keys)
    markup.add('Отмена')
    await bot.send_message(callback_query.from_user.id, "Ты вернулся назад, выбери точку снова",
                           reply_markup=markup)
    await state.set_state('place_change')  # Используйте нужную команду для смены состояния


# @dp.message_handler(commands='update_table', state='*')
async def update_table_handler(message: types.Message, state: FSMContext):
    await message.answer("Команда больше недоступна")
    # async with state.proxy() as data:
    #     authorized_user = data.get('authorized_user')
    #     if authorized_user:
    #         await state.update_data(authorized_user=authorized_user)
    #         markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    #         for keys in worksheets:
    #             markup.add(keys)
    #         markup.add('Отмена')
    #         await message.answer("Выбери точку, на которой работал: ", reply_markup=markup)
    #         await state.set_state("place_change")
    #     else:
    #         await message.reply("Ты не авторизован. Введи свой логин и пароль с помощью команды /auth")


# @dp.message_handler(state='place_change')
async def place_change(message: types.Message, state: FSMContext):
    if message.text == "Отмена":
        await message.answer('Команда отменена, воспользуйся ей ещё раз, что бы начать сначала')
        await state.reset_state(with_data=False)
    else:
        async with state.proxy() as data:
            place = message.text
            for key in worksheets:
                if key == place:
                    data['place'] = place
            inline_keyboard = await get_inline_keyboard(state=state)
            await message.answer('Теперь выбери дату за которую хочешь внести: ', reply_markup=inline_keyboard)
            await state.set_state('date_trying')


# @dp.callback_query_handler(lambda c: c.data and c.data.startswith('date_'), state='date_trying')
async def date_trying(callback_query: types.CallbackQuery, state: FSMContext):
    current_date = callback_query.data[5:]
    try:
        async with state.proxy() as data:
            place = data.get('place')
            for key in worksheets:
                if key == place:
                    current_worksheet = worksheets.get(key)
            dates = current_worksheet.col_values(2)
            indexes = []
            for dat in dates:
                if dat == current_date:
                    indexes.append(dates.index(dat) + 1)
            data['first'] = indexes[0]
            if place in not_full_day:
                data['second'] = indexes[1] + 1
            if place in not_full_day:
                options = ['Утренняя', 'Вечерняя', 'Назад', 'Отмена']
                markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                for option in options:
                    markup.add(KeyboardButton(option))
                await callback_query.message.answer("Теперь выбери смену в которую ты работал",
                                                    reply_markup=markup)
                await state.set_state('work_change')
            else:
                first = data.get('first')
                data['current_index'] = first
                for key in worksheet_names:
                    if key == place:
                        current_worksheet_names = worksheet_names.get(key)
                names = current_worksheet_names.col_values(19)
                del names[0]
                name_list = []
                for name in names:
                    if name != '':
                        name_list.append(name)
                markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                for option in name_list:
                    markup.add(KeyboardButton(option))
                markup.add('Назад')
                markup.add('Отмена')
                await callback_query.message.answer('Выбери своё имя и фамилию, или введи вручную',
                                                    reply_markup=markup)
                await state.set_state('name_change')
    except Exception:
        await callback_query.message.answer("Произошла ошибка, поставь задачу в квант с подробным описанием проблемы"
                                            " и скиншотом")


# @dp.message_handler(state='work_change')
async def work_change(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        first = data.get('first')
        second = data.get('second')
        place = data.get('place')
        if message.text == 'Назад':
            inline_keyboard = await get_inline_keyboard(state=state)
            await message.answer('Выбери дату снова:', reply_markup=inline_keyboard)
            await state.set_state('date_trying')
        elif message.text == "Отмена":
            await message.answer("Команда отменена, воспользуйся ей ещё раз, что бы начать сначала")
            await state.reset_state(with_data=False)
        elif message.text == 'Утренняя':
            data['current_index'] = first
            for key in worksheet_names:
                if key == place:
                    current_worksheet_names = worksheet_names.get(key)
            names = current_worksheet_names.col_values(19)
            del names[0]
            name_list = []
            for name in names:
                if name != '':
                    name_list.append(name)
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            for option in name_list:
                markup.add(KeyboardButton(option))
            markup.add('Назад')
            markup.add('Отмена')
            await message.answer('Выбери своё имя и фамилию, или введи вручную', reply_markup=markup)
            await state.set_state('name_change')
        elif message.text == 'Вечерняя':
            data['current_index'] = second
            for key in worksheet_names:
                if key == place:
                    current_worksheet_names = worksheet_names.get(key)
            names = current_worksheet_names.col_values(19)
            del names[0]
            name_list = []
            for name in names:
                if name != '':
                    name_list.append(name)
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for option in name_list:
                markup.add(KeyboardButton(option))
            markup.add('Назад')
            markup.add('Отмена')
            await message.answer('Выбери своё имя и фамилию, или введи вручную', reply_markup=markup)
            await state.set_state('name_change')
        else:
            await message.answer("Некорректный ввод")


# @dp.message_handler(state='name_change')
async def name_change(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        inline_keyboard = await get_inline_keyboard(state=state)
        await message.answer('Снова выбери дату за которую хочешь внести: ', reply_markup=inline_keyboard)
        await state.set_state('date_trying')
    elif message.text == "Отмена":
        await message.answer("Команда отменена, воспользуйся ей ещё раз, что бы начать сначала")
        await state.reset_state(with_data=False)
    else:
        async with state.proxy() as data:
            data['name'] = message.text
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Назад')
            markup.add("Отмена")
            await message.answer("Теперь введи наличку", reply_markup=markup)
            await state.set_state('money')


# @dp.message_handler(state='money')
async def money_change(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        money = message.text
        if money == "Назад":
            place = data.get('place')
            for key in worksheet_names:
                if key == place:
                    current_worksheet_names = worksheet_names.get(key)
            names = current_worksheet_names.col_values(19)
            del names[0]
            name_list = []
            for name in names:
                if name != '':
                    name_list.append(name)
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for option in name_list:
                markup.add(KeyboardButton(option))
            markup.add('Назад')
            markup.add("Отмена")
            await message.answer('Выбери своё имя и фамилию, или введи вручную',
                                 reply_markup=markup)
            await state.set_state('name_change')
        elif money == "Отмена":
            await message.answer("Команда отменена, воспользуйся ей ещё раз, что бы начать сначала")
            await state.reset_state(with_data=False)
        elif money.isnumeric():
            data['money'] = int(money)
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Назад')
            markup.add('Отмена')
            await message.answer("Теперь введи безнал", reply_markup=markup)
            await state.set_state('bank_money')
        else:
            await message.answer("Введи число друг")


# @dp.message_handler(state='bank_money')
async def bank_money_change(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        bank_money = message.text
        if bank_money == 'Назад':
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Назад')
            markup.add("Отмена")
            await message.answer("Снова введи наличку", reply_markup=markup)
            await state.set_state('money')
        elif bank_money == 'Отмена':
            await message.answer("Команда отменена, воспользуйся ей ещё раз, что бы начать сначала")
            await state.reset_state(with_data=False)
        elif bank_money.isnumeric():
            data['bank_money'] = int(bank_money)
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Назад')
            markup.add("Отмена")
            await message.answer("Теперь введи расходы", reply_markup=markup)
            await state.set_state('expenses')
        else:
            await message.answer("Введи число друг")


# @dp.message_handler(state='expenses')
async def expences_change(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        expenses = message.text
        if expenses == 'Назад':
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Назад')
            markup.add("Отмена")
            await message.answer("Снова введи безнал", reply_markup=markup)
            await state.set_state('bank_money')
        elif expenses == "Отмена":
            await message.answer("Команда отменена, воспользуйся ей ещё раз, что бы начать сначала")
            await state.reset_state(with_data=False)
        elif expenses.isnumeric():
            data['expenses'] = int(expenses)
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Назад')
            markup.add("Отмена")
            await message.answer("Теперь введи кол-во чеков", reply_markup=markup)
            await state.set_state('check_count')
        else:
            await message.answer("Введи число друг")


# @dp.message_handler(state='check_count')
async def check_count_change(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        check_count = message.text
        if check_count == 'Назад':
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Назад')
            await message.answer("Снова введи расходы", reply_markup=markup)
            await state.set_state('expenses')
        elif check_count == "Отмена":
            await message.answer("Команда отменена, воспользуйся ей ещё раз, что бы начать сначала")
            await state.reset_state(with_data=False)
        elif check_count.isnumeric():
            data['check_count'] = check_count
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Назад')
            markup.add("Отмена")
            await message.answer("Ну и осталось ввести инкассацию", reply_markup=markup)
            await state.set_state('collection')
        else:
            await message.answer("Введи число друг")


# @dp.message_handler(state='collection')
async def collection_change(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        collection = message.text
        if collection == 'Назад':
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Назад')
            markup.add("Отмена")
            await message.answer("Снова введи количество чеков", reply_markup=markup)
            await state.set_state('check_count')
        elif collection == "Отмена":
            await message.answer("Команда отменена, воспользуйся ей ещё раз, что бы начать сначала")
            await state.reset_state(with_data=False)
        elif collection.isnumeric():
            data['collection'] = collection
            current_index = data.get('current_index')
            place = data.get('place')
            for key in worksheets:
                if key == place:
                    current_worksheet = worksheets.get(key)
            await message.answer("Таблица обновляется")
            place = data.get('place')
            current_worksheet.update(f'O{current_index}', data.get('name'))
            current_worksheet.update(f'Q{current_index}', int(data.get('money')))
            current_worksheet.update(f'S{current_index}', int(data.get('bank_money')))
            current_worksheet.update(f'W{current_index}', int(data.get('expenses')))
            current_worksheet.update(f'Y{current_index}', int(data.get('check_count')))
            current_worksheet.update(f'AA{current_index}', int(data.get('collection')))
            await message.answer("Таблица обновлена успешно")
            await state.reset_state(with_data=False)
        else:
            await message.answer("Введи число друг")


def register_handlers_money_tables(dp: Dispatcher):
    dp.register_message_handler(update_table_handler, commands='update_table', state='*')
    dp.register_message_handler(place_change, state='place_change')
    dp.register_callback_query_handler(date_trying, lambda c: c.data and c.data.startswith('date_'),
                                       state='date_trying')
    dp.register_message_handler(work_change, state='work_change')
    dp.register_callback_query_handler(cancel_calendar, text="cancel_calendar", state="*")
    dp.register_callback_query_handler(go_back_to_start, text='back_to_start', state='*')
    dp.register_message_handler(name_change, state='name_change')
    dp.register_message_handler(money_change, state='money')
    dp.register_message_handler(bank_money_change, state='bank_money')
    dp.register_message_handler(expences_change, state='expenses')
    dp.register_message_handler(check_count_change, state='check_count')
    dp.register_message_handler(collection_change, state='collection')
