import sqlite3
import os
import json

DB_PATH = 'cards.db'

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT DEFAULT '',
                        rank TEXT DEFAULT 'Участник',
                        first_name TEXT DEFAULT ''
                    )''')

    # Таблица карточек
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_cards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        card_id INTEGER NOT NULL,
                        drop_time TEXT NOT NULL,
                        quantity INTEGER DEFAULT 1,
                        FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )''')

    conn.commit()
    conn.close()

# Проверяем существование базы данных
if not os.path.exists(DB_PATH):
    create_db()

def add_card(user_id, card_id, drop_time, quantity=1):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO user_cards (user_id, card_id, drop_time, quantity)
                      VALUES (?, ?, ?, ?)''', (user_id, card_id, drop_time, quantity))
    conn.commit()
    conn.close()

def remove_all_cards(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM user_cards WHERE user_id = ?''', (user_id,))
    conn.commit()
    conn.close()

def remove_card(user_id, card_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM user_cards WHERE user_id = ? AND card_id = ?''', (user_id, card_id))
    conn.commit()
    conn.close()

def update_card_quantity(user_id, card_id, quantity):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''UPDATE user_cards SET quantity = ? WHERE user_id = ? AND card_id = ?''', (quantity, user_id, card_id))
    conn.commit()
    conn.close()

def get_user_cards(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Выполняем SQL-запрос для получения всех карточек пользователя
    cursor.execute('''
        SELECT card_id, drop_time, quantity
        FROM user_cards
        WHERE user_id = ?
    ''', (user_id,))

    # Извлекаем все карточки пользователя
    cards = cursor.fetchall()

    # Преобразуем результат в список словарей
    cards_list = [{"card_id": card[0], "drop_time": card[1], "quantity": card[2]} for card in cards]

    # Преобразуем список в строку JSON
    cards_json = json.dumps(cards_list, ensure_ascii=False, indent=4)

    # Закрываем соединение с базой данных
    conn.close()

    return cards_json
