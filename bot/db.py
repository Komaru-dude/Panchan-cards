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
                        rank TEXT DEFAULT 'Гость',
                        first_name TEXT DEFAULT '',
                        coins INTEGER DEFAULT 0,
                        gems INTEGER DEFAULT 0,
                        next_card_time TEXT DEFAULT '2000-01-01 00:00:00'
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

# Функция для проверки ранга пользователя
def has_permission(user_id, level):
    # Словарь с уровнями и соответствующими рангами
    rank_to_level = {
        "Забанен": 0,
        "Гость": 1,
        "Активный": 2,
        "Администратор": 3,
    }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Извлекаем ранг пользователя
    cursor.execute('''SELECT rank FROM users WHERE user_id = ?''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        return False
    
    user_rank = result[0]  # Получаем статус пользователя
    user_level = rank_to_level.get(user_rank)
    
    if user_level is None:
        return False  # Если ранг не найден в словаре, возвращаем False

    return user_level >= level  # Проверяем, соответствует ли уровень пользователя требуемому

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

def get_user_cards(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT card_id, drop_time, quantity
        FROM user_cards
        WHERE user_id = ?
    ''', (user_id,))
    cards = cursor.fetchall()
    cards_list = [{"card_id": card[0], "drop_time": card[1], "quantity": card[2]} for card in cards]
    cards_json = json.dumps(cards_list, ensure_ascii=False, indent=4)
    conn.close()
    return cards_json

def add_user(user_id, username='', rank='Гость', first_name=''):
    """Добавление нового пользователя в базу данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    username = username.lower()
    cursor.execute('''INSERT INTO users (user_id, username, rank, first_name)
                      VALUES (?, ?, ?, ?)''', (user_id, username, rank, first_name))
    conn.commit()
    conn.close()

def user_exists(user_id):
    """Проверка существования пользователя в базе данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT 1 FROM users WHERE user_id = ? LIMIT 1''', (user_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def reset_cooldown(user_id):
    """Сбрасывает время кулдауна для пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    old_date = "2000-01-01 00:00:00"  # Устанавливаем значение сброса
    cursor.execute('''UPDATE users SET next_card_time = ? WHERE user_id = ?''', (old_date, user_id))
    conn.commit()
    conn.close()

def get_data(user_id, mode="one", field=""):
    """
    Извлекает данные из таблицы users.
    :param user_id: ID пользователя
    :param mode: Режим работы ("one" для одного поля, "all" для всех данных пользователя)
    :param field: Название поля (только для mode="one")
    :return: Значение поля (mode="one") или все данные пользователя (mode="all")
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if mode == "one":
        if not field:
            raise RuntimeError("Нужно указать поле перед извлечением данных")
        cursor.execute(f'''SELECT {field} FROM users WHERE user_id = ?''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None  # Возвращаем значение поля или None, если пользователь отсутствует

    elif mode == "all":
        cursor.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result  # Возвращаем все данные пользователя или None

    else:
        conn.close()
        raise RuntimeError("Такого режима не существует")
    
def set_data(user_id, field, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f'''UPDATE users SET {field} = ? WHERE user_id = ?''', (data, user_id))
    conn.commit()
    conn.close()

def get_next_drop_time(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''SELECT next_card_time FROM users WHERE user_id = ?''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result