from modules import questions_ttk
questions_dict = questions_ttk.questions

import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = '6285611257:AAGcsm_qWuJKPJsWlpdTX9kGiyKKDOU5DS4'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# Список категорий вопросов
categories = questions_dict.keys()

# Словарь вопросов и ответов
questions = questions_dict.values()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item = KeyboardButton("Training")
    markup.add(item)
    await message.answer("Hi! I am your quiz bot. Type /training to start training.", reply_markup=markup)


@dp.message_handler(commands=['training'])
async def start_training(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        item = KeyboardButton(category)
        markup.add(item)
    await message.answer("Choose a category:", reply_markup=markup)


@dp.message_handler(lambda message: message.text in categories)
async def choose_difficulty(message: types.Message):
    category = message.text
    if category in questions:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for difficulty in ["5 questions", "10 questions", "20 questions"]:
            item = KeyboardButton(difficulty)
            markup.add(item)
        await message.answer(f"Choose difficulty level for {category}:", reply_markup=markup)
    else:
        await message.answer("Sorry, no questions available for this category.")


@dp.message_handler(lambda message: message.text in ["5 questions", "10 questions", "20 questions"])
async def start_quiz(message: types.Message):
    category = message.text.split()[0]
    difficulty = int(message.text.split()[0])
    if category in questions and difficulty > 0:
        selected_questions = random.sample(questions[category].keys(), min(difficulty, len(questions[category])))
        for q in selected_questions:
            await ask_question(message.chat.id, category, q, questions[category][q])
    else:
        await message.answer("Invalid selection. Please try again.")


async def ask_question(chat_id, category, question, options):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for option in options["options"]:
        item = KeyboardButton(option)
        markup.add(item)

    await bot.send_message(chat_id, f"{category} - {question}", reply_markup=markup)


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

