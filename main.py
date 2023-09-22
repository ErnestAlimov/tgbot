import logging
import random
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.types import ParseMode
from aiogram.utils import executor

from db import Database

API_TOKEN = '5984776234:AAHaAjQQFwRH1lH_oDWXuTuX8XX3a4XFdzQ'  

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
db = Database()  


active_codes = {}



def generate_invite_code():
    code = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(6))
    return code



@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    invite_code = active_codes.get(user_id)

    if not invite_code:
        invite_code = generate_invite_code()
        active_codes[user_id] = invite_code

    await message.reply(f'Привет! Твой инвайт-код: {invite_code}\nПоделись им с друзьями, чтобы пригласить их.')



@dp.message_handler(commands=['invite'])
async def invite(message: types.Message):
    user_id = message.from_user.id
    invite_code = active_codes.get(user_id)

    if invite_code:
        await message.reply(f'Твой инвайт-код: {invite_code}\nПоделись им с друзьями, чтобы пригласить их.')
    else:
        await message.reply('У тебя пока нет активного инвайт-кода. Используй /start, чтобы получить его.')



@dp.message_handler(lambda message: message.text.isdigit() and len(message.text) == 6)
async def process_invite_code(message: types.Message):
    user_id = message.from_user.id
    invite_code = message.text

    if db.is_invite_code_valid(invite_code):
        referrer_id = db.get_referrer_id(invite_code)
        db.save_invitation(referrer_id, user_id)
        await message.reply('Ты успешно зарегистрировался с инвайт-кодом!')
    else:
        await message.reply('Неверный инвайт-код. Попробуй еще раз.')


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
