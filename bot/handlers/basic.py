import os, json, random
from aiogram import Router, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from bot import db

base_router = Router()

CARDS_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'media', 'cards_info.json')
TRIGGER_PHRASES_PATH = os.path.join(os.path.dirname(__file__), '..', 'media', 'trigger_phrases.txt')

def load_cards():
    try:
        with open(CARDS_JSON_PATH, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise RuntimeError(f"Не удалось найти файл {CARDS_JSON_PATH}")
    except json.JSONDecodeError:
        raise RuntimeError(f"Ошибка чтения JSON в {CARDS_JSON_PATH}")

cards_data = load_cards()

def load_trigger_phrases():
    try:
        with open(TRIGGER_PHRASES_PATH, 'r', encoding='utf-8') as file:
            return {line.strip().lower() for line in file if line.strip()}
    except FileNotFoundError:
        raise RuntimeError(f"Не удалось найти файл {TRIGGER_PHRASES_PATH}")

trigger_phrases = load_trigger_phrases()

RARITY_PROBABILITIES = {
    "common": 50,
    "rare": 25,
    "epic": 15,
    "mythic": 8,
    "legendary": 2
}

def get_random_card():
    rarities = list(RARITY_PROBABILITIES.keys())
    weights = list(RARITY_PROBABILITIES.values())
    selected_rarity = random.choices(rarities, weights, k=1)[0]

    available_cards = [card for card in cards_data if card['rarity'] == selected_rarity]
    if not available_cards:
        raise RuntimeError(f"Нет доступных карточек для редкости {selected_rarity}")
    return random.choice(available_cards)

def can_receive_card(user_id):
    next_drop = db.get_next_drop_time(user_id)
    if not next_drop:
        return True

    next_drop_time = next_drop[0] if isinstance(next_drop, tuple) else next_drop

    try:
        last_drop_time = datetime.strptime(next_drop_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise RuntimeError(f"Неверный формат времени последнего дропа: {next_drop_time}")

    return datetime.now() - last_drop_time >= timedelta(hours=12)

@base_router.message(Command("start"))
async def cmd_start(message: types.Message):
    first_name = message.from_user.first_name
    await message.reply(f"👋 Привет {first_name},\n\n"
                        "💡 Для начала рекомендую ознакомиться с инстаграммом хозяйки: https://www.instagram.com/tansoku_love/\n\n"
                        "📝 Чтобы получить карту напишите \"качан\", \"панчан\", \"дай карту\" или /get_card\n\n"
                        "📱 Создатель бота @komaru_dude\n"
                        "🧨 Гитхаб: https://github.com/Komaru-dude/Panchan-cards")

@base_router.message(Command("get_card"))
async def cmd_get_card(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    if not db.user_exists(user_id):
        db.add_user(user_id, username, first_name=first_name)

    user_rank = db.get_data(user_id, field="rank")
    if user_rank == "Забанен":
        return

    if not can_receive_card(user_id):
        await message.reply("Вы уже получали карточку за последние 12 часов. Попробуйте позже!")
        return

    try:
        card = get_random_card()
    except RuntimeError as e:
        await message.reply(f"Ошибка: {e}")
        return

    drop_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.add_card(user_id, card['id'], drop_time)
    next_drop_time = datetime.now() + timedelta(hours=12)
    db.set_data(user_id, "next_card_time", next_drop_time.strftime('%Y-%m-%d %H:%M:%S'))

    card_image_path = os.path.join(os.path.dirname(__file__), '..', 'media', 'cards', card['picture_name'])
    if not os.path.exists(card_image_path):
        await message.reply(f"Изображение карточки {card['picture_name']} не найдено.")
        return

    photo = FSInputFile(card_image_path)
    await message.reply_photo(photo, caption=f"💪 У вас новая карточка: \n\n"
                                             f"👤 Имя: {card['name']}\n"
                                             f"💎 Редкость: {card['rarity'].capitalize()}")

@base_router.message(Command("profile"))
async def cmd_profile(message: types.Message):
    user_id = message.from_user.id

    if not db.user_exists(user_id):
        await message.reply("Вы ещё не зарегистрированы. Используйте команду /start.")
        return

    userdata = db.get_data(user_id, mode="all")
    if userdata is None:
        await message.reply("Ошибка: данные пользователя не найдены.")
        return

    rank, first_name, unique_cards, coins, gems = userdata[2], userdata[3], userdata[4] or 0, userdata[5], userdata[6]
    total_cards = len(cards_data)

    await message.reply(f"📜 **Ваш профиль**\n\n"
                        f"👤 Имя: {first_name or 'Не указано'}\n"
                        f"⚙️ Ранг: {rank}\n"
                        f"🃏 Уникальных карточек: {unique_cards}/{total_cards}\n"
                        f"💰 Монет: {coins}\n"
                        f"💎 Кристаллов: {gems}\n", parse_mode=ParseMode.MARKDOWN_V2)
