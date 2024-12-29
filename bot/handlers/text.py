import json
import os
import random
from datetime import datetime, timedelta
from aiogram import Router, types
from bot import db

text_router = Router()

# Загрузка данных о карточках
CARDS_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'media', 'cards_info.json')

def load_cards():
    with open(CARDS_JSON_PATH, 'r', encoding='utf-8') as file:
        return json.load(file)

cards_data = load_cards()

# Шансы выпадения карточек по редкости
RARITY_PROBABILITIES = {
    "common": 50,
    "rare": 25,
    "epic": 15,
    "mythic": 8,
    "legendary": 2
}

# Определение карточки по вероятностям
def get_random_card():
    rarities = list(RARITY_PROBABILITIES.keys())
    weights = list(RARITY_PROBABILITIES.values())
    selected_rarity = random.choices(rarities, weights, k=1)[0]

    available_cards = [card for card in cards_data if card['rarity'] == selected_rarity]
    return random.choice(available_cards)

# Проверка, прошло ли 12 часов с последнего дропа
def can_receive_card(user_id):
    last_drop = db.get_last_drop_time(user_id)
    if not last_drop:
        return True

    last_drop_time = datetime.strptime(last_drop, '%Y-%m-%d %H:%M:%S')
    return datetime.now() - last_drop_time >= timedelta(hours=12)

@text_router.message(F.text)
async def text(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    # Добавление пользователя в базу, если его там нет
    if not db.user_exists(user_id):
        db.add_user(user_id, username, first_name=first_name)

    # Проверка, может ли пользователь получить карточку
    if not can_receive_card(user_id):
        await message.reply("Вы уже получали карточку за последние 12 часов. Попробуйте позже!")
        return

    # Выдача карточки
    card = get_random_card()
    drop_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.add_card(user_id, card['id'], drop_time)

    # Отправка информации пользователю
    card_image_path = os.path.join(os.path.dirname(__file__), '..', 'media', 'cards', card['picture_name'])
    with open(card_image_path, 'rb') as photo:
        await message.reply_photo(photo, caption=f"Поздравляем! Вы получили карточку: \n\n"
                                   f"Название: {card['name']}\n"
                                   f"Редкость: {card['rarity'].capitalize()}")