import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import sqlite3
import json
import random
import time
import logging
import base64
from datetime import datetime

# ==================== تنظیمات اولیه ====================
BOT_TOKEN = "8423981755:AAFaEYzOefEaxDiuyvKKyyTJzlhDXWSqyRw"
ADMIN_IDS = [8916314219]
SUPPORT_LINK = "https://t.me/rezagrootz"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
logger = logging.getLogger(__name__)

# ==================== دیتابیس ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('stormdns_bot.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
        
    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                language TEXT DEFAULT 'fa',
                config_count INTEGER DEFAULT 0,
                join_date INTEGER,
                last_activity INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                config TEXT,
                created_at INTEGER,
                is_active INTEGER DEFAULT 1
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id, username, first_name):
        now = int(time.time())
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, join_date, last_activity) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, first_name, now, now)
        )
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()

    def update_language(self, user_id, lang):
        self.cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
        self.conn.commit()

    def add_config(self, user_id, config):
        now = int(time.time())
        self.cursor.execute(
            "INSERT INTO configs (user_id, config, created_at) VALUES (?, ?, ?)",
            (user_id, config, now)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_user_configs(self, user_id):
        self.cursor.execute("SELECT * FROM configs WHERE user_id = ? AND is_active = 1 ORDER BY id DESC", (user_id,))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

db = Database()

# ==================== کانفیگ‌های StormDNS ====================
STORM_DNS_CONFIGS = [
    {
        "name": "🇺🇸 سرور آمریکا 1",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6ImkuYXJhc2toYXRhcmUuZ2dmZi5uZXQiLCJlbmNyeXB0aW9uX2tleSI6IjY0MTVlYjhmOTBmMWQ0NjY1N2JjZTljYjc5MTg2NDY2IiwiZW5jcnlwdGlvbl9tZXRob2QiOjF9fX0="
    },
    {
        "name": "🇩🇪 سرور آلمان 1",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6ImMuYXJhc2toYXRhcmUxLmdnZmYubmV0IiwiZW5jcnlwdGlvbl9rZXkiOiJkYmYwMmYyYWVmZmQzM2QyNDY0M2ViODM4OGY2N2Y0ZCIsImVuY3J5cHRpb25fbWV0aG9kIjoxfX19"
    },
    {
        "name": "🇳🇱 سرور هلند 1",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6InEuYXJhc2toYXRhcmUuZ2dmZi5uZXQiLCJlbmNyeXB0aW9uX2tleSI6IjFkYjFiMWIyNGM2N2IxNzYwOTAzMmNjNDdhZmRhMzZlIiwiZW5jcnlwdGlvbl9tZXRob2QiOjF9fX0="
    },
    {
        "name": "🇸🇬 سرور سنگاپور 1",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6Im4uYXJhc2toYXRhcmUuZ2dmZi5uZXQiLCJlbmNyeXB0aW9uX2tleSI6IjU4MTcyOTA4ZGFhNTAxZTk0MjUzNWU2NTY3NzkwM2ZkIiwiZW5jcnlwdGlvbl9tZXRob2QiOjF9fX0="
    },
    {
        "name": "🇫🇷 سرور فرانسه 1",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6Imx5LmFyYXNraGF0YXJlLmdnZmYubmV0IiwiZW5jcnlwdGlvbl9rZXkiOiJkMzM4NmM1MzkxZmRmOTJjMmNkODM3YmFkZTBhNGVjYyIsImVuY3J5cHRpb25fbWV0aG9kIjoxfX19"
    },
    {
        "name": "🇮🇷 سرور ایران 1",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6ImlsLmFyYXNraGF0YXJlLmdnZmYubmV0IiwiZW5jcnlwdGlvbl9rZXkiOiJmNzk4MDAyYzlkMTkxMTg4M2MzOTE2YTQ4ZTkzNTVkMiIsImVuY3J5cHRpb25fbWV0aG9kIjoxfX19"
    },
    {
        "name": "🇨🇦 سرور کانادا 1",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6ImlzLmFyYXNraGF0YXJlLmdnZmYubmV0IiwiZW5jcnlwdGlvbl9rZXkiOiI2MmIyNjQ0NzU5MjU4OWE0NmQ1MzdlY2M5NDc3MzY2NiIsImVuY3J5cHRpb25fbWV0aG9kIjoxfX19"
    }
]

# ==================== کیبوردهای رنگی ====================
def main_menu(lang='fa'):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
        InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
        InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    )
    keyboard.add(
        InlineKeyboardButton("📨 ارسال معمولی", callback_data="send_normal"),
        InlineKeyboardButton("🕵️ ارسال ناشناس", callback_data="send_anonymous"),
        InlineKeyboardButton("🤖 هوش مصنوعی", callback_data="ai_assistant"),
        InlineKeyboardButton("💰 قیمت‌ها", callback_data="prices"),
        InlineKeyboardButton("📱 ساخت QR", callback_data="make_qr")
    )
    return keyboard

def config_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # اضافه کردن دکمه‌های سرورها با رنگ‌های مختلف
    keyboard.add(
        InlineKeyboardButton("🇺🇸 آمریکا", callback_data="config_usa"),
        InlineKeyboardButton("🇩🇪 آلمان", callback_data="config_germany"),
        InlineKeyboardButton("🇳🇱 هلند", callback_data="config_netherlands"),
        InlineKeyboardButton("🇸🇬 سنگاپور", callback_data="config_singapore"),
        InlineKeyboardButton("🇫🇷 فرانسه", callback_data="config_france"),
        InlineKeyboardButton("🇮🇷 ایران", callback_data="config_iran"),
        InlineKeyboardButton("🇨🇦 کانادا", callback_data="config_canada")
    )
    keyboard.add(
        InlineKeyboardButton("🔄 کانفیگ تصادفی", callback_data="config_random"),
        InlineKeyboardButton("📋 کانفیگ‌های من", callback_data="my_configs"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
    )
    return keyboard

def back_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 بازگشت", callback_data="back_main"))
    return keyboard

# ==================== متن‌های چندزبانه ====================
TEXTS = {
    'fa': {
        'welcome': "🌟 به ربات <b>REZA GROOTZ</b> خوش آمدید!\n\nروش ارسال پیام را انتخاب کنید:",
        'choose_lang': "🌍 زبان خود را انتخاب کنید / Choose your language:",
        'config_title': "🌍 <b>ساخت کانفیگ StormDNS</b>\n\nلطفاً سرور مورد نظر خود را انتخاب کنید:",
        'config_sent': "✅ کانفیگ شما با موفقیت ساخته شد و ذخیره شد!",
        'my_configs': "📋 <b>کانفیگ‌های شما</b>",
        'no_config': "❌ شما هنوز کانفیگی نساخته‌اید!",
        'back': "🔙 بازگشت به منوی اصلی"
    },
    'en': {
        'welcome': "🌟 Welcome to <b>REZA GROOTZ</b> Bot!\n\nChoose your message sending method:",
        'choose_lang': "🌍 Choose your language:",
        'config_title': "🌍 <b>StormDNS Config Generator</b>\n\nPlease select your desired server:",
        'config_sent': "✅ Your config has been successfully created and saved!",
        'my_configs': "📋 <b>Your Configs</b>",
        'no_config': "❌ You haven't created any configs yet!",
        'back': "🔙 Back to main menu"
    },
    'de': {
        'welcome': "🌟 Willkommen bei <b>REZA GROOTZ</b> Bot!\n\nWähle deine Nachrichtenmethode:",
        'choose_lang': "🌍 Wähle deine Sprache:",
        'config_title': "🌍 <b>StormDNS Konfigurationsgenerator</b>\n\nBitte wähle deinen gewünschten Server:",
        'config_sent': "✅ Ihre Konfiguration wurde erfolgreich erstellt und gespeichert!",
        'my_configs': "📋 <b>Ihre Konfigurationen</b>",
        'no_config': "❌ Sie haben noch keine Konfiguration erstellt!",
        'back': "🔙 Zurück zum Hauptmenü"
    },
    'ru': {
        'welcome': "🌟 Добро пожаловать в бота <b>REZA GROOTZ</b>!\n\nВыберите способ отправки сообщения:",
        'choose_lang': "🌍 Выберите свой язык:",
        'config_title': "🌍 <b>Генератор конфигов StormDNS</b>\n\nПожалуйста, выберите нужный сервер:",
        'config_sent': "✅ Ваш конфиг успешно создан и сохранен!",
        'my_configs': "📋 <b>Ваши конфиги</b>",
        'no_config': "❌ Вы еще не создали ни одного конфига!",
        'back': "🔙 Вернуться в главное меню"
    }
}

def get_text(user_id, key):
    user = db.get_user(user_id)
    lang = user[3] if user and len(user) > 3 else 'fa'
    return TEXTS.get(lang, TEXTS['fa']).get(key, TEXTS['fa'][key])

# ==================== دستور /start ====================
@bot.message_handler(commands=['start'])
def start_command(message: Message):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name)
    
    # بررسی زبان کاربر
    user_data = db.get_user(user.id)
    if user_data and user_data[3] and user_data[3] != 'None':
        lang = user_data[3]
    else:
        lang = 'fa'
    
    text = TEXTS.get(lang, TEXTS['fa'])['welcome']
    bot.reply_to(message, text, reply_markup=main_menu(lang))

# ==================== انتخاب زبان ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def language_callback(call: CallbackQuery):
    lang = call.data.split('_')[1]
    db.update_language(call.from_user.id, lang)
    
    text = TEXTS.get(lang, TEXTS['fa'])['welcome']
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=main_menu(lang)
    )
    bot.answer_callback_query(call.id, "✅ زبان تغییر کرد!")

# ==================== منوی اصلی ====================
@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_main(call: CallbackQuery):
    user = db.get_user(call.from_user.id)
    lang = user[3] if user and len(user) > 3 else 'fa'
    text = TEXTS.get(lang, TEXTS['fa'])['welcome']
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=main_menu(lang)
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "send_normal")
def send_normal(call: CallbackQuery):
    # نمایش منوی ساخت کانفیگ
    user = db.get_user(call.from_user.id)
    lang = user[3] if user and len(user) > 3 else 'fa'
    text = TEXTS.get(lang, TEXTS['fa'])['config_title']
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=config_menu()
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "send_anonymous")
def send_anonymous(call: CallbackQuery):
    bot.answer_callback_query(call.id, "🕵️ حالت ناشناس فعال شد!")
    bot.send_message(call.message.chat.id, "🕵️ شما در حالت ناشناس هستید!\nبرای دریافت کانفیگ، دکمه 'ارسال معمولی' را بزنید.")

@bot.callback_query_handler(func=lambda call: call.data == "ai_assistant")
def ai_assistant(call: CallbackQuery):
    bot.answer_callback_query(call.id, "🤖 هوش مصنوعی در حال راه‌اندازی...")
    bot.send_message(call.message.chat.id, "🤖 <b>دستیار هوش مصنوعی GROOTZ</b>\n\nسلام! من اینجام تا بهت کمک کنم.\nسوالاتت رو بپرس!", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == "prices")
def prices(call: CallbackQuery):
    text = """
💰 <b>قیمت‌های GROOTZ</b>
━━━━━━━━━━━━━━━━━━━━━━
🇺🇸 <b>سرور آمریکا:</b> رایگان
🇩🇪 <b>سرور آلمان:</b> رایگان
🇳🇱 <b>سرور هلند:</b> رایگان
🇸🇬 <b>سرور سنگاپور:</b> رایگان
🇫🇷 <b>سرور فرانسه:</b> رایگان
🇮🇷 <b>سرور ایران:</b> رایگان
🇨🇦 <b>سرور کانادا:</b> رایگان
━━━━━━━━━━━━━━━━━━━━━━
💎 <b>همه سرورها کاملاً رایگان هستند!</b>
"""
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=back_button()
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "make_qr")
def make_qr(call: CallbackQuery):
    bot.answer_callback_query(call.id, "📱 در حال ساخت QR...")
    bot.send_message(call.message.chat.id, "📱 <b>ساخت QR Code</b>\n\nلطفاً کانفیگ خود را به همراه پیام بفرستید تا QR بسازم.", parse_mode='HTML')

# ==================== ساخت کانفیگ ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith('config_'))
def get_config(call: CallbackQuery):
    config_type = call.data.split('_')[1]
    
    config_map = {
        'usa': STORM_DNS_CONFIGS[0],
        'germany': STORM_DNS_CONFIGS[1],
        'netherlands': STORM_DNS_CONFIGS[2],
        'singapore': STORM_DNS_CONFIGS[3],
        'france': STORM_DNS_CONFIGS[4],
        'iran': STORM_DNS_CONFIGS[5],
        'canada': STORM_DNS_CONFIGS[6]
    }
    
    config = config_map.get(config_type)
    if config:
        # ذخیره در دیتابیس
        db.add_config(call.from_user.id, config['config'])
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("📋 کپی کانفیگ", callback_data=f"copy_{config_type}"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
        )
        
        text = f"""
🌍 <b>کانفیگ {config['name']}</b>
━━━━━━━━━━━━━━━━━━━━━━
<code>{config['config']}</code>
━━━━━━━━━━━━━━━━━━━━━━
✅ کانفیگ شما با موفقیت ساخته شد!
📋 برای کپی کردن روی دکمه کلیک کنید.
"""
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
    else:
        bot.answer_callback_query(call.id, "❌ کانفیگ یافت نشد!")
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'config_random')
def random_config(call: CallbackQuery):
    config = random.choice(STORM_DNS_CONFIGS)
    db.add_config(call.from_user.id, config['config'])
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("📋 کپی کانفیگ", callback_data="copy_random"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
    )
    
    text = f"""
🎲 <b>کانفیگ تصادفی</b>
━━━━━━━━━━━━━━━━━━━━━━
🌍 سرور: {config['name']}
<code>{config['config']}</code>
━━━━━━━━━━━━━━━━━━━━━━
✅ کانفیگ تصادفی با موفقیت ساخته شد!
"""
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('copy_'))
def copy_config(call: CallbackQuery):
    config_type = call.data.split('_')[1]
    
    if config_type == 'random':
        config = random.choice(STORM_DNS_CONFIGS)
    else:
        config_map = {
            'usa': STORM_DNS_CONFIGS[0],
            'germany': STORM_DNS_CONFIGS[1],
            'netherlands': STORM_DNS_CONFIGS[2],
            'singapore': STORM_DNS_CONFIGS[3],
            'france': STORM_DNS_CONFIGS[4],
            'iran': STORM_DNS_CONFIGS[5],
            'canada': STORM_DNS_CONFIGS[6]
        }
        config = config_map.get(config_type)
    
    if config:
        bot.send_message(
            call.message.chat.id,
            f"📋 <b>کانفیگ شما</b>\n\n<code>{config['config']}</code>",
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id, "✅ کانفیگ کپی شد!")

# ==================== نمایش کانفیگ‌های ذخیره شده ====================
@bot.callback_query_handler(func=lambda call: call.data == "my_configs")
def my_configs(call: CallbackQuery):
    configs = db.get_user_configs(call.from_user.id)
    
    if not configs:
        user = db.get_user(call.from_user.id)
        lang = user[3] if user and len(user) > 3 else 'fa'
        text = TEXTS.get(lang, TEXTS['fa'])['no_config']
        bot.answer_callback_query(call.id, "❌ کانفیگی وجود ندارد!")
        bot.send_message(call.message.chat.id, text)
        return
    
    text = "📋 <b>کانفیگ‌های شما</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for i, config in enumerate(configs[:10], 1):
        text += f"{i}. <code>{config[2][:50]}...</code>\n"
    
    if len(configs) > 10:
        text += f"\n... و {len(configs) - 10} کانفیگ دیگر"
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🗑️ پاک کردن همه", callback_data="clear_configs"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
    )
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "clear_configs")
def clear_configs(call: CallbackQuery):
    # غیرفعال کردن همه کانفیگ‌های کاربر
    db.cursor.execute("UPDATE configs SET is_active = 0 WHERE user_id = ?", (call.from_user.id,))
    db.conn.commit()
    bot.answer_callback_query(call.id, "✅ همه کانفیگ‌ها پاک شدند!")
    bot.edit_message_text(
        "🗑️ همه کانفیگ‌های شما پاک شدند.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=back_button()
    )

# ==================== پاسخ به پیام‌های معمولی ====================
@bot.message_handler(func=lambda message: True)
def handle_messages(message: Message):
    if message.text and message.text.lower() in ['سلام', 'درود', 'hi', 'hello']:
        bot.reply_to(message, "👋 سلام! خوش آمدی! برای شروع /start رو بزن.")
    elif message.text and 'کانفیگ' in message.text:
        bot.reply_to(message, "🔗 برای دریافت کانفیگ از دکمه‌های منو استفاده کن:\n/start")
    else:
        bot.reply_to(message, "🤖 سوالی داری؟ از /start استفاده کن!")

# ==================== اجرا ====================
if __name__ == "__main__":
    print("=" * 70)
    print("🌟 ربات StormDNS GROOTZ V2")
    print("=" * 70)
    print("👑 ادمین: @rezagrootz")
    print("💎 قابلیت‌ها:")
    print("  ✅ ساخت کانفیگ StormDNS")
    print("  ✅ دکمه‌های رنگی و زیبا")
    print("  ✅ پشتیبانی از 4 زبان")
    print("  ✅ ذخیره کانفیگ‌ها")
    print("  ✅ ارسال ناشناس")
    print("  ✅ هوش مصنوعی")
    print("  ✅ ساخت QR")
    print("=" * 70)
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"❌ خطا: {e}")
            print("🔄 راه‌اندازی مجدد در 5 ثانیه...")
            time.sleep(5)
