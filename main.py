from create_bot import dp
from aiogram import executor
from modules import key, ttk_test, yoballs, avans, money_tables


key.register_handlers_key(dp)
ttk_test.register_handlers_ttk(dp)
yoballs.register_handlers_yoball(dp)
# avans.register_handlers_avans(dp)
money_tables.register_handlers_money_tables(dp)


executor.start_polling(dp, skip_updates=True)
