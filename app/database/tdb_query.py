import sqlite3


def create_db():
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = cursor.fetchone()

    if not table_exists:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                status TEXT
            )
        ''')
        conn.commit()
        print("Таблица 'users' была создана.")
    else:
        print("Таблица 'users' уже существует.")
    conn.close()


def is_user_in_db(user_id):
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user is not None


def add_user_to_db(user_id, chat_id, status='active'):
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_id, chat_id, status) VALUES (?, ?, ?)',
                   (user_id, chat_id, status))
    conn.commit()
    conn.close()
