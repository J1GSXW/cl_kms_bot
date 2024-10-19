import json
from create_bot import bot
import sqlite3 as sq

with (open('data.json', 'r') as file):
    data = json.load(file)


def db_save_user_id(user_id):
    with sq.connect("Cof_Like_bot.db") as con:
        cur = con.cursor()
        sq_insert = f"""INSERT INTO users_ud_for_tg (tg_id)
                    VALUES(?);"""
        data_turple = (user_id,)
        cur.execute(sq_insert, data_turple)


def save_user_id(user_id):
    if user_id not in data['users']:
        data['users'].append(user_id)
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)
            db_save_user_id(user_id)

# async def on_start(dp):
#     # Отправка уведомления всем пользователям
#     for user_id in data['users']:
#         await bot.send_message(user_id, "Привет друг, бот был перезапущен, пожалуйста, воспользуйся командой /auth,"
#                                         " что бы войти заново")
