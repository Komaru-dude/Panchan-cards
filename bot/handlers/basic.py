from aiogram import Router
from aiogram import types

base_router = Router()

@base_router.message()
async def cmd_start(message: types.Message):
    await message.reply("Приве брадок")