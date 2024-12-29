from aiogram import Router, types
from aiogram.filters import Command

base_router = Router()

@base_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("Приве брадок")