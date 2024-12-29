from aiogram import Router, types
from aiogram.filters import Command
from bot import db

adm_router = Router()

@adm_router.message(Command("reset_cooldown"))
async def cmd_rc(message: types.Message):
    user_id = message.from_user.id
    if not db.has_permission(user_id, 3):
        await message.reply("Вы не имеете прав для выполнения этой команды.")
        return
    
    target_user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
    
    try:
        db.reset_cooldown(target_user_id)
        await message.reply(f"Кулдаун получения карточки сброшен для пользователя с ID: {target_user_id}")
    except:
        await message.reply(f"Не удалось сбросить кулдаун для пользователя с ID: {target_user_id}")

@adm_router.message(Command("ban"))
async def cmd_ban(message: types.Message):
    user_id = message.from_user.id
    if not db.has_permission(user_id, 3):
        await message.reply("Вы не имеете прав для выполнения этой команды.")
        return
    
    target_user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
    
    try:
        db.set_data(target_user_id, "rank", "Забанен")
        await message.reply(f"Пользователь (ID: {target_user_id}) был заблокирован")
    except Exception as e:
        await message.reply(f"Не удалось заблокировать пользователя(ID: {target_user_id}).\n Ошибка: {e}")

@adm_router.message(Command("unban"))
async def cmd_unban(message: types.Message):
    user_id = message.from_user.id
    if not db.has_permission(user_id, 3):
        await message.reply("Вы не имеете прав для выполнения этой команды.")
        return
    
    target_user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
    
    try:
        db.set_data(target_user_id, "rank", "Участник")
        await message.reply(f"Пользователь (ID: {target_user_id}) был разблокирован")
    except Exception as e:
        await message.reply(f"Не удалось разблокировать пользователя(ID: {target_user_id}).\n Ошибка: {e}")