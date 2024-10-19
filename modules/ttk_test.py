import random
from aiogram import Dispatcher
from create_bot import dp, bot
from aiogram import types
from aiogram import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from modules import key, questions_ttk

questions = questions_ttk.questions


admins = ['ИА', 'МС']



difficulty_levels = {
    "Легкий(5 вопросов)": 5,
    "Средний(10 вопросов)": 10,
    "Сложный(20 вопросов)": 20
}


current_category = None
current_question = None
correct_answer = None
answered_correctly = 0



async def start_training(message: types.Message, state: FSMContext):
    await message.answer("Этот блок сейчас дорабатывается, после найденных ошибок. В скором времени он заработает")
    # async with state.proxy() as data:
    #     authorized_user = data.get('authorized_user')
    #     authtorizer_user_find = data.get('login')
    #     users = key.db_get_user_login()
    #     if authorized_user and authtorizer_user_find in users:
    #         global current_category, current_question, correct_answer, answered_correctly, total_questions
    #
    #         keyboard = types.InlineKeyboardMarkup(row_width=1)
    #         for category in questions.keys():
    #             keyboard.add(types.InlineKeyboardButton(text=category, callback_data=f"category:{category}"))
    #         keyboard.add(types.InlineKeyboardButton(text="Все", callback_data="category:all"))
    #
    #         await message.reply("Выбери категорию:", reply_markup=keyboard)
    #         current_question = iter([])
    #         current_category = None
    #         answered_correctly = 0
    #         total_questions = 0
    #     else:
    #         await message.reply("Ты не авторизован. Введи свой логин и пароль с помощью команды /auth")


def get_random_questions_from_all():
    all_questions = []
    for category_questions in questions.values():
        all_questions.extend(category_questions.keys())
    return random.sample(all_questions, total_questions)

async def ask_next_question(chat_id):
    global current_category, current_question, correct_answer

    if current_category is None:
        await bot.send_message(chat_id, "Выбери категорию.")
        return

    try:
        if current_category == "all":
            question = next(current_question)
            category = next(filter(lambda c: question in questions[c], questions.keys()))
        else:
            question = next(current_question)
            category = current_category

        variants = list(questions[category][question].keys())
        random.shuffle(variants)
        correct_answer = variants.index(next(filter(lambda k: questions[category][question][k], questions[category][question].keys())))
        markup = types.InlineKeyboardMarkup(row_width=1)
        for index, variant in enumerate(variants):
            markup.add(types.InlineKeyboardButton(text=variant, callback_data=str(index)))
        await bot.send_message(chat_id, f"Вопрос: {question}", reply_markup=markup)
    except StopIteration:
        await bot.send_message(chat_id, f"Тестик окончен. Правильно отвечено: {answered_correctly} из {total_questions}")
        reset_quiz()

def reset_quiz():
    global current_category, current_question, correct_answer
    current_question = iter([])
    current_category = None
    correct_answer = None

async def process_selection(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        authorized_user = data.get('authorized_user')
        authtorizer_user_find = data.get('login')
        users = key.db_get_user_login()
        if authorized_user and authtorizer_user_find in users:
            global current_category, current_question, correct_answer, total_questions

            category = query.data.split(':')[1]
            if category == 'all':
                current_category = 'all'
                current_question = iter(get_random_questions_from_all())
            else:
                current_category = category

            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for difficulty, num_questions in difficulty_levels.items():
                keyboard.add(types.InlineKeyboardButton(text=difficulty, callback_data=f"difficulty:{num_questions}"))
            await bot.send_message(query.message.chat.id, "Выбери уровень сложности:", reply_markup=keyboard)
        else:
            await query.message.reply("Ты не авторизован. Введи свой логин и пароль с помощью команды /auth")


# @dp.callback_query_handler(lambda query: query.data.startswith('difficulty:'))
async def process_difficulty(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        authorized_user = data.get('authorized_user')
        authtorizer_user_find = data.get('login')
        users = key.db_get_user_login()
        if authorized_user and authtorizer_user_find in users:
            global current_question, correct_answer, total_questions

            num_questions = int(query.data.split(':')[1])
            total_questions = num_questions

            if current_category == 'all':
                current_question = iter(get_random_questions_from_all())
            else:
                category_questions = questions[current_category]
                if len(category_questions) < total_questions:
                    await bot.send_message(query.message.chat.id, "В этой категории не хватает вопросов. Пожалуйста, выбери другую сложность.")
                    return
                current_question = iter(random.sample(list(category_questions.keys()), total_questions))

            await ask_next_question(query.message.chat.id)
        else:
            await query.message.reply("Ты не авторизован. Введи свой логин и пароль с помощью команды /auth")




# @dp.callback_query_handler()
async def process_answer(call: types.CallbackQuery, state:FSMContext):
    async with state.proxy() as data:
        authorized_user = data.get('authorized_user')
        authtorizer_user_find = data.get('login')
        users = key.db_get_user_login()
        if authorized_user and authtorizer_user_find in users:
            global current_question, correct_answer, answered_correctly

            if call.data == 'disabled':
                return

            selected_option = call.message.reply_markup.inline_keyboard[int(call.data)][0].text
            correct_option = call.message.reply_markup.inline_keyboard[correct_answer][0].text

            if int(call.data) == correct_answer:
                answered_correctly += 1
                await call.answer("Правильно, ты красавчик!")
                await call.message.reply(f"Правильно, ты красавчик! Ты выбрал вариант: {selected_option}")
            else:
                await call.answer("Неправильно :( Повтори ещё раз ТТК пожалуйста!")
                await call.message.reply(f"Неправильно :( Повтори ещё раз ТТК пожалуйста!\nТы выбрал вариант: {selected_option}.\nВерный вариант: {correct_option}")

            await ask_next_question(call.message.chat.id)

            # Отключение кнопок после выбора ответа
            keyboard = call.message.reply_markup
            if keyboard:
                for row in keyboard.inline_keyboard:
                    for button in row:
                        button['callback_data'] = 'disabled'
                await call.message.edit_reply_markup(keyboard)
        else:
            await call.message.reply("Ты не авторизован. Введи свой логин и пароль с помощью команды /auth")



def register_handlers_ttk(dp: Dispatcher):
    dp.register_message_handler(start_training, commands="training", state='*')
    dp.register_callback_query_handler(process_selection, lambda query: query.data.startswith('category:'))
    dp.register_callback_query_handler(process_difficulty, lambda query: query.data.startswith('difficulty:'))
    dp.register_callback_query_handler(process_answer)



