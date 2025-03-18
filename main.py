from order import *
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update, ReplyKeyboardRemove,BotCommand
from user import get_user_language, get_user, save_user_info, save_user_phone
from Dictionaries import translations
from profile import get_user_profile


TOKEN = "TOKEN"
GROUP_CHAT_ID = ID

ASK_ORDER_TEXT, ASK_ORDER_PHOTOS = range(2)

# **Bazaga buyurtmalarni saqlash uchun o'zgaruvchi**
order_messages = {}  # {guruh_message_id: user_id}

def set_bot_commands(bot):
    """Botga buyruqlarni o‘rnatish"""
    commands = [
        BotCommand("start", "Botni ishga tushirish / Запустить бота"),
        BotCommand("info", "Bot haqida ma'lumot / Информация о боте")

    ]
    bot.set_my_commands(commands)  # ✅ TO‘G‘RI: `bot` obyektini ishlatish kerak


def start_handler(update, context):
    user_id = update.message.chat_id
    user = get_user(user_id)  # Foydalanuvchini tekshiramiz
    if user:  # Agar user mavjud bo‘lsa
        language = user[0]  # Tilini olish
        user_lang = translations[language]

        # ** Asosiy menyu tugmalari **
        menu_keyboard = [
            [user_lang["profile"], user_lang["order"]],
            [user_lang["change_language"]]
        ]
        reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

        # Matn + tugmalar bilan javob berish
        update.message.reply_text(user_lang["already_registered"], reply_markup=reply_markup)
    else:
        show_language_selection(update)

def show_language_selection(update):
    keyboard = [
        ["🇬🇦 Qaraqalpaq tili", "🇺🇿 O'zbek tili"],
        ["🇷🇺 Русский язык"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(translations["uz"]["choose_language"], reply_markup=reply_markup)

def language_selection(update, context):
    user_id = update.message.chat_id
    text = update.message.text

    languages = {
        "🇬🇦 Qaraqalpaq tili": "kk",
        "🇺🇿 O'zbek tili": "uz",
        "🇷🇺 Русский язык": "ru"
    }

    # ❌ Profile tugmasi bosilganda bu kod ishlamasligi kerak
    if text not in languages:
        return

    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    username = update.message.chat.username
    language = languages[text]

    # Ma'lumotni bazaga saqlaymiz
    save_user_info(user_id, first_name, last_name, username, language)

    user_lang = translations[language]
    contact_button = KeyboardButton(user_lang["send_phone"], request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)
    update.message.reply_text(user_lang["ask_phone"], reply_markup=reply_markup)


def profile_handler(update, context):
    user_id = update.message.chat_id
    user_profile = get_user_profile(user_id)

    if user_profile:
        user_lang = translations[user_profile["language"]]

        profile_text = (
            f"{user_lang['profile_info']}\n"
            f"👤 {user_lang['name']}: {user_profile['first_name']} {user_profile['last_name']}\n"
            f"🔹 {user_lang['username_telegram']}: @{user_profile['username']}\n"
            f"📞 {user_lang['phone_number']}: {user_profile['phone_number']}\n"
            f"🌍 {user_lang['language']}: {user_profile['language'].upper()}"
        )
        update.message.reply_text(profile_text)
    else:
        update.message.reply_text(translations["uz"]["not_registered"])  # Default: Uzbek tili

# 🔹 Foydalanuvchining tiliga qarab "Profil" tugmasini tekshirish
def profile_button_handler(update, context):
    user_id = update.message.chat_id
    user_lang_code = get_user_language(user_id)  # Foydalanuvchining tilini olish
    user_lang = translations.get(user_lang_code, translations["uz"])  # Default: uzbek tili
    text = update.message.text

    if text == user_lang["profile"]:
        profile_handler(update, context)
    elif text == user_lang["order"]:
        order_start(update, context)  # ✅ Buyurtma jarayonini boshlash
    elif text == user_lang["change_language"]:
        change_language_handler(update, context)


def change_language_handler(update, context):
    user_id = update.message.chat_id
    show_language_selection(update)  # Tilni qaytadan tanlash


def save_contact(update, context):
    user_id = update.message.chat_id
    contact = update.message.contact
    language = get_user_language(user_id)  # Foydalanuvchining tilini olish

    if contact:
        save_user_phone(user_id, contact.phone_number)
        user_lang = translations[language]

        update.message.reply_text(user_lang["phone_saved"])

        # Asosiy menyu (Tilga qarab tugmalar)
        menu_keyboard = [
            [user_lang["profile"], user_lang["order"]],
            [user_lang["change_language"]]
        ]
        # reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)
        reply_markup = ReplyKeyboardMarkup(menu_keyboard,resize_keyboard=True, reply_markup = ReplyKeyboardRemove())

        update.message.reply_text(user_lang["welcome"], reply_markup=reply_markup)


# **Zakaz berish jarayoni boshlanadi**
def order_start(update, context):
    user_id = update.message.chat_id
    user_lang_code = get_user_language(user_id)
    user_lang = translations.get(user_lang_code, translations["uz"])  # Default: uzbek tili

    update.message.reply_text(user_lang["ask_order_text"], parse_mode="Markdown")
    return ASK_ORDER_TEXT




# **Zakaz matnini qabul qilish**
def order_text(update, context):
    context.user_data["order_text"] = update.message.text
    context.user_data["media"] = []  # Rasmlar yoki fayllarni saqlash uchun bo'sh ro‘yxat

    # # ✅ Tasdiqlash tugmasini qo‘shish
    user_id = update.message.chat_id
    user_lang_code = get_user_language(user_id)
    user_lang = translations.get(user_lang_code, translations["uz"])

    update.message.reply_text(user_lang["waiting_two"],
                              parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    return ASK_ORDER_PHOTOS


# **Zakaz rasmlar va fayllarni qabul qilish**
def order_photos(update, context):
    user_id = update.message.chat_id
    user_lang_code = get_user_language(user_id)
    user_lang = translations.get(user_lang_code, translations["uz"])
    if "media" not in context.user_data:
        context.user_data["media"] = []

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        context.user_data["media"].append(InputMediaPhoto(media=file_id))
    elif update.message.document:
        file_id = update.message.document.file_id
        context.user_data["media"].append(InputMediaDocument(media=file_id))

    update.message.reply_text(user_lang["waiting"], parse_mode="Markdown")

# **Tasdiqlash va guruhga yuborish**
def confirm_order(update, context):
    user = update.message.from_user
    user_lang_code = get_user_language(user.id)
    user_lang = translations.get(user_lang_code, translations["uz"])  # Default: uzbek tili
    user_data = get_user_profile(user.id)


    if not user_data:
        update.message.reply_text(user_lang["profile_not_found"])
        return ConversationHandler.END

    # ⚠️ user_data dictionary formatida kelmoqda, shuning uchun undan qiymatlarni to'g'ri olish kerak
    first_name = user_data.get("first_name", "N/A")
    last_name = user_data.get("last_name", "N/A")
    username = user_data.get("username", "N/A")
    phone = user_data.get("phone_number", "N/A")  # ⚠️ Bu yerda 'phone_number' deb yozish kerak!

    order_text = context.user_data.get("order_text", user_lang["no_text"])
    media_group = context.user_data.get("media", [])

    if not media_group:
        update.message.reply_text(user_lang["no_media"])
        return ASK_ORDER_PHOTOS

    caption = (
        f"{user_lang['new_order']}\n\n"
        f"👤 {user_lang['name']}: {first_name}\n"
        f"👥 {user_lang['surname']}: {last_name}\n"
        f"🔗 {user_lang['username']}: @{username if username != 'N/A' else user_lang['not_available']}\n"
        f"📞 {user_lang['phone']}: {phone}\n\n"
        f"📝 {user_lang['order_details']}:\n{order_text}"
    )

    # Birinchi rasm/faylga caption qo‘shiladi
    media_group[0].caption = caption
    media_group[0].parse_mode = "Markdown"

    # Rasmlar/fayllarni jo‘natish
    sent_message = context.bot.send_media_group(chat_id=GROUP_CHAT_ID, media=media_group)

    for msg in sent_message:
        order_messages[msg.message_id] = user.id

    # ✅ Buyurtma qabul qilindi, endi "Orqaga" tugmasi chiqadi
    back_button = KeyboardButton(user_lang["back"])
    reply_markup = ReplyKeyboardMarkup([[back_button]], resize_keyboard=True)

    update.message.reply_text(user_lang["order_accepted"], reply_markup=reply_markup)
    return ConversationHandler.END

def back_handler(update, context):
    """🔙 "Orqaga" tugmasi bosilganda foydalanuvchini asosiy menyuga qaytarish."""
    user_id = update.message.chat_id
    user_lang_code = get_user_language(user_id)
    user_lang = translations.get(user_lang_code, translations["uz"])  # Default: uzbek tili

    # **Asosiy menyu** tugmalarini yaratish
    menu_keyboard = [
        [KeyboardButton(user_lang["profile"]), KeyboardButton(user_lang["order"])],
        [KeyboardButton(user_lang["change_language"])]
    ]
    reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

    # ✅ Agar "back_to_main" mavjud bo‘lmasa, default matnni ishlatamiz
    back_text = user_lang.get("back_to_main", "🔙 Asosiy menyu")
    update.message.reply_text(back_text, reply_markup=reply_markup)
    # ✅ ConversationHandler.END qaytariladi, shunda state tugaydi
    return ConversationHandler.END

# **Bekor qilish funksiyasi**
def cancel(update, context):
    update.message.reply_text("🔙 Buyurtma berish bekor qilindi.")
    return ConversationHandler.END

def infomessage(update, context):
    update.message.reply_text("📢 FotoPro bot haqqında maǵlıwmat 📢\n"
                              "FotoPro - bul sizdiń súwretlerińizdi professional tárzde redaktorlaw ushın arnawlı islep shıǵılǵan bot! 🎨✨\n"
                              "🛠 Xızmetlerimiz:\n"
                              "✅ Eski súwretlerdi qayta tiklew hám sapasın asırıw - 80 000 so'm\n"
                              "✅ Fon almastırıw hám suwretlerdi shıraylı dizaynǵa jaylastırıw - 50 000 so'm\n"
                              "✅ Logo hám banner dizayni jaratıw - 50 000 so'm\n"
                              "✅ Toy hám basqa arnawlı ilajlar ushın foto albom montaj qılıw - 80 000 so'm\n"
                              "\n📤 Qanday isleydi?\n"
                              "1️⃣ Súwretlerińizdi júkleń\n"
                              "2️⃣ Talaplarıńızdı jazıń \n"
                              "3️⃣ Biziń dizaynerler suwretińizdi sapalı islewge ótkeredi\n"
                              "4️⃣ Tayın nátiyjeni alasız!\n"
                              "💰 Xızmet haqi jumıs juwmaqlanǵanınan keyin talap etiledi. Jumıstıń quramalılıǵına qaray bahalar ózgeriwi múmkin. Tolıq maǵlıwmat ushın admınıstrator menen baylanısıń. 😊\n"
                              "---------------------------\n"
                              "📢 FotoPro bot haqida ma'lumot 📢\n"

                              "FotoPro – bu sizning rasmlaringizni professional tarzda tahrirlash uchun maxsus ishlab chiqilgan bot! 🎨✨\n"

                              "🛠 Xizmatlarimiz:\n"
                              "✅ Eski rasmlarni tiklash va sifatini oshirish – 80 000 so‘m\n"
                              "✅ Fon almashtirish va tasvirlarni chiroyli dizaynga joylashtirish – 50 000 so‘m\n"
                              "✅ Logo va banner dizayni yaratish – 50 000 so‘m\n"
                              "✅ To‘y va boshqa maxsus tadbirlar uchun foto albom montaj qilish – 80 000 so‘m\n"

                              "\n📤 Qanday ishlaydi?\n"
                              "1️⃣ Rasmlaringizni yuklang\n"
                              "2️⃣ Talablaringizni yozing\n"
                              "3️⃣ Bizning dizaynerlar rasmingizni sifatli ishlovdan o'tkazadi\n"
                              "4️⃣ Tayyor natijani olasiz!\n"

                              "💰 Xizmat haqi ish yakunlanganidan so‘ng talab qilinadi. Ishning murakkabligiga qarab narxlar o‘zgarishi mumkin. Batafsil ma’lumot uchun administrator bilan bog‘laning.😊\n"
                              "---------------------------\n"
                              "📢 Информация о боте FotoPro 📢\n"

                              "FotoPro – это бот, созданный для профессиональной обработки ваших фотографий! 🎨✨"

                              "🛠 Наши услуги:\n"
                              "✅ Восстановление старых фотографий и улучшение качества – 80 000 сум\n"
                              "✅ Замена фона и стильная обработка изображений – 50 000 сум\n"
                              "✅ Создание логотипов и баннерного дизайна – 50 000 сум\n"
                              "✅ Монтаж фотоальбомов для свадеб и других особых событий – 80 000 сум\n"

                              "\n📤 Как это работает?\n"
                              "1️⃣ Загрузите свои фотографии\n"
                              "2️⃣ Опишите свои пожелания\n"
                              "3️⃣ Наши дизайнеры профессионально обработают ваше изображение\n"
                              "4️⃣ Получите готовый результат!\n"

                              "💰 Оплата услуг производится после завершения работы. Цена может варьироваться в зависимости от сложности заказа. Для уточнения деталей свяжитесь с администратором. 😊")


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # 📌 Bot buyruqlarini o‘rnatish
    set_bot_commands(updater.bot)

    dispatcher.add_handler(CommandHandler('start', start_handler))
    dispatcher.add_handler(CommandHandler('info', infomessage))
    # 🔹 **Profil tugmasini ajratib olish** (Regex orqali)
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(👤 Profil|👤 Профиль|👤 Profil)$'), profile_button_handler)),
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(🔙 Назад|🔙 Orqaga|🔙 arqaǵa)$'), back_handler))
    order_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(r'.*(🛒 Buyırtpa beriw|🛒 Оформить заказ|🛒 Buyurtma berish|order).*'), order_start)],
        states={
            ASK_ORDER_TEXT: [
                MessageHandler(Filters.text & ~Filters.command, order_text)
            ],
            ASK_ORDER_PHOTOS: [
                MessageHandler(Filters.photo | Filters.document, order_photos),
                MessageHandler(Filters.regex(r'^(\+|confirm)$'), confirm_order)
                # Orqaga tugmasini qo‘shish
            ],
        },
        fallbacks=[MessageHandler(Filters.regex(r'^(❌ Bekor qilish|❌ Бас тарту|❌ Отмена)$'), cancel)]
    )
    dispatcher.add_handler(order_handler)
    # 🔹 **Tilni o'zgartirish tugmasi**
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(Tildi ózgertiw|Tilni o‘zgartirish|Изменить язык|change_language)$'), change_language_handler))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, language_selection))
    dispatcher.add_handler(MessageHandler(Filters.contact, save_contact))



    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
