import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            language TEXT,
            phone_number TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user_info(user_id, first_name, last_name, username, language):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, first_name, last_name, username, language)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, first_name, last_name, username, language))
    conn.commit()
    conn.close()

def save_user_phone(user_id, phone_number):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET phone_number = ? WHERE user_id = ?
    """, (phone_number, user_id))
    conn.commit()
    conn.close()

def save_user_language(user_id, language):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)", (user_id, language))
    conn.commit()
    conn.close()

def get_user_language(user_id):
    """Foydalanuvchining tanlagan tilini bazadan olish"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "uz"  # Default: Uzbek tili

def get_user(user_id):
    """Foydalanuvchi bazada bor-yo‘qligini tekshiradi"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user  # Agar user mavjud bo‘lsa, (language,) tuple qaytadi, aks holda None

init_db()
