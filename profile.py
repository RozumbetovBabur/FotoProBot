from telegram import Update
from telegram.ext import CallbackContext
from user import get_user_language
from Dictionaries import translations
import sqlite3
def get_user_profile(user_id):
    """Foydalanuvchining profili uchun ma’lumotlarni olish"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, last_name, username, phone_number, language FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "first_name": user[0],
            "last_name": user[1],
            "username": user[2],
            "phone_number": user[3],
            "language": user[4]
        }
    else:
        return None


