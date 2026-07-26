import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import sqlite3
import json
import random
import string
import time
import logging
import threading
import requests
import base64
from datetime import datetime, timedelta

# ==================== تنظیمات اولیه ====================
BOT_TOKEN = "8810741889:AAF9h94CG7dmkvJRd3SHNH1npwezAi2wQ1A"  # توکن ربات شما
ADMIN_IDS = [8916314219]  # آیدی عددی شما
SUPPORT_CHANNEL = "@rezagrootz"  # کانال پشتیبانی
BOT_USERNAME = "REZA_GROOTZ_BOT"  # یوزرنیم ربات

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')
logger = logging.getLogger(__name__)

# ==================== دیتابیس پیشرفته ====================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('config_bot.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()
        
    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                config_count INTEGER DEFAULT 0,
                join_date INTEGER,
                last_activity INTEGER,
                is_premium INTEGER DEFAULT 0,
                configs TEXT DEFAULT '[]'
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                config TEXT,
                created_at INTEGER,
                expires_at INTEGER,
                is_active INTEGER DEFAULT 1,
                note TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                host TEXT,
                port INTEGER,
                uuid TEXT,
                path TEXT,
                sni TEXT,
                public_key TEXT,
                short_id TEXT,
                type TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                server_id INTEGER,
                config TEXT,
                status TEXT DEFAULT 'pending',
                created_at INTEGER,
                paid_at INTEGER
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

    def add_config(self, user_id, config):
        now = int(time.time())
        expires = now + 30 * 86400  # 30 روز اعتبار
        self.cursor.execute(
            "INSERT INTO configs (user_id, config, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (user_id, config, now, expires)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_user_configs(self, user_id):
        self.cursor.execute("SELECT * FROM configs WHERE user_id = ? AND is_active = 1", (user_id,))
        return self.cursor.fetchall()

    def get_all_users(self):
        self.cursor.execute("SELECT user_id FROM users")
        return [row[0] for row in self.cursor.fetchall()]

    def close(self):
        self.conn.close()

db = Database()

# ==================== کانفیگ‌های آماده ====================
PREMIUM_CONFIGS = [
    {
        "name": "🇺🇸 آمریکا - پرسرعت",
        "config": "vless://e51796bb-3305-ac88-f39d-22fd9dd63b4f@130.49.77.3:443?encryption=none&security=reality&sni=cdn.steamstatic.com&fp=chrome&pbk=3DYkxUg9fBA6cONioJOPrsklcMQEImEsurR6air4swo&allowInsecure=1&sid=&type=xhttp&host=cdn.steamstatic.com&path=/&mode=auto#🇺🇸_REZA_GROOTZ"
    },
    {
        "name": "🇩🇪 آلمان - پایدار",
        "config": "vless://e51796bb-3305-ac88-f39d-22fd9dd63b4f@130.49.77.3:443?encryption=none&security=reality&sni=cdn.steamstatic.com&fp=chrome&pbk=3DYkxUg9fBA6cONioJOPrsklcMQEImEsurR6air4swo&allowInsecure=1&sid=&type=xhttp&host=cdn.steamstatic.com&path=/&mode=auto#🇩🇪_REZA_GROOTZ"
    },
    {
        "name": "🇳🇱 هلند - ضد فیلتر",
        "config": "vless://e51796bb-3305-ac88-f39d-22fd9dd63b4f@130.49.77.3:443?encryption=none&security=reality&sni=cdn.steamstatic.com&fp=chrome&pbk=3DYkxUg9fBA6cONioJOPrsklcMQEImEsurR6air4swo&allowInsecure=1&sid=&type=xhttp&host=cdn.steamstatic.com&path=/&mode=auto#🇳🇱_REZA_GROOTZ"
    },
    {
        "name": "🇸🇬 سنگاپور - کم پینگ",
        "config": "vless://e51796bb-3305-ac88-f39d-22fd9dd63b4f@130.49.77.3:443?encryption=none&security=reality&sni=cdn.steamstatic.com&fp=chrome&pbk=3DYkxUg9fBA6cONioJOPrsklcMQEImEsurR6air4swo&allowInsecure=1&sid=&type=xhttp&host=cdn.steamstatic.com&path=/&mode=auto#🇸🇬_REZA_GROOTZ"
    },
    {
        "name": "🇫🇷 فرانسه - سریع",
        "config": "vless://e51796bb-3305-ac88-f39d-22fd9dd63b4f@130.49.77.3:443?encryption=none&security=reality&sni=cdn.steamstatic.com&fp=chrome&pbk=3DYkxUg9fBA6cONioJOPrsklcMQEImEsurR6air4swo&allowInsecure=1&sid=&type=xhttp&host=cdn.steamstatic.com&path=/&mode=auto#🇫🇷_REZA_GROOTZ"
    }
]

# ==================== کیبوردهای رنگی و فوق‌پیشرفته ====================
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎯 دریافت کانفیگ رایگان", callback_data="free_config"),
        InlineKeyboardButton("💎 دریافت کانفیگ ویژه", callback_data="premium_config"),
        InlineKeyboardButton("🪄 دریافت سرور اختصاصی GROOTZ", callback_data="dedicated_server"),
        InlineKeyboardButton("📊 وضعیت سرورها", callback_data="server_status"),
        InlineKeyboardButton("🆘 راهنما و پشتیبانی", url="https://t.me/rezagrootz"),
        InlineKeyboardButton("📢 کانال ما", url="https://t.me/rezagrootz"),
        InlineKeyboardButton("👤 پروفایل من", callback_data="profile"),
        InlineKeyboardButton("⭐️ ربات را حمایت کنید", callback_data="support_bot")
    )
    return keyboard

def config_type_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🇺🇸 آمریکا", callback_data="config_usa"),
        InlineKeyboardButton("🇩🇪 آلمان", callback_data="config_germany"),
        InlineKeyboardButton("🇳🇱 هلند", callback_data="config_netherlands"),
        InlineKeyboardButton("🇸🇬 سنگاپور", callback_data="config_singapore"),
        InlineKeyboardButton("🇫🇷 فرانسه", callback_data="config_france"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
    )
    return keyboard

def premium_config_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("💎 کانفیگ طلایی", callback_data="premium_gold"),
        InlineKeyboardButton("👑 کانفیگ الماس", callback_data="premium_diamond"),
        InlineKeyboardButton("🌟 کانفیگ پلاتینیوم", callback_data="premium_platinum"),
        InlineKeyboardButton("🪄 کانفیگ اختصاصی", callback_data="premium_custom"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
    )
    return keyboard

def admin_panel():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 آمار ربات", callback_data="admin_stats"),
        InlineKeyboardButton("📨 ارسال همگانی", callback_data="admin_broadcast"),
        InlineKeyboardButton("👥 لیست کاربران", callback_data="admin_users"),
        InlineKeyboardButton("⚙️ تنظیمات", callback_data="admin_settings"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
    )
    return keyboard

# ==================== توابع کمکی ====================
def is_admin(user_id):
    return user_id in ADMIN_IDS

def generate_subscription_link(user_id):
    return f"https://t.me/{BOT_USERNAME}?start=sub_{user_id}"

def format_config(config_string):
    """فرمت‌بندی کانفیگ برای نمایش زیبا"""
    lines = config_string.split('?')
    if len(lines) > 1:
        main_part = lines[0]
        params = lines[1].split('&')
        formatted = f"<b>🔗 لینک کانفیگ:</b>\n<code>{config_string}</code>\n\n"
        formatted += "<b>📋 پارامترها:</b>\n"
        for param in params:
            if '=' in param:
                k, v = param.split('=', 1)
                formatted += f"▫️ <b>{k}:</b> {v}\n"
        return formatted
    return f"<code>{config_string}</code>"

def get_config_by_name(name):
    for config in PREMIUM_CONFIGS:
        if config["name"] == name:
            return config["config"]
    return None

# ==================== دستور /start ====================
@bot.message_handler(commands=['start'])
def start_command(message: Message):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name)
    
    # بررسی ریفرال
    if len(message.text.split()) > 1:
        ref_id = message.text.split()[1]
        if ref_id.startswith('sub_'):
            # کاربر از لینک اشتراک آمده
            pass
    
    welcome_text = f"""
🌟 <b>به ربات فوق‌پیشرفته GROOTZ خوش آمدید!</b> 🌟

🔥 <b>قابلیت‌های بی‌نظیر:</b>
✅ دریافت کانفیگ V2Ray با کیفیت بالا
✅ سرورهای اختصاصی و پرسرعت
✅ پشتیبانی ۲۴ ساعته
✅ کانفیگ‌های ضد فیلتر و پایدار
✅ کاملاً رایگان و سریع

🪄 <b>برای دریافت کانفیگ، از دکمه‌های زیر استفاده کنید:</b>

👤 <b>کاربر:</b> {user.first_name}
🆔 <b>آیدی:</b> <code>{user.id}</code>
"""
    bot.reply_to(message, welcome_text, reply_markup=main_menu())

# ==================== دستور /admin ====================
@bot.message_handler(commands=['admin'])
def admin_command(message: Message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ شما دسترسی به این بخش ندارید!")
        return
    bot.reply_to(message, "👑 <b>پنل مدیریت ربات</b>", reply_markup=admin_panel())

# ==================== کال‌بک‌های اصلی ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id
    data = call.data
    
    # ========== منوی اصلی ==========
    if data == "back_main":
        bot.edit_message_text("🌟 <b>منوی اصلی</b>", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
        bot.answer_callback_query(call.id)
        return
    
    if data == "free_config":
        bot.edit_message_text("🌍 <b>سرورهای رایگان</b>\nلطفاً سرور مورد نظر خود را انتخاب کنید:", 
                            call.message.chat.id, call.message.message_id, reply_markup=config_type_menu())
        bot.answer_callback_query(call.id)
        return
    
    if data == "premium_config":
        bot.edit_message_text("💎 <b>کانفیگ‌های ویژه و پرسرعت</b>\nانتخاب کنید:", 
                            call.message.chat.id, call.message.message_id, reply_markup=premium_config_menu())
        bot.answer_callback_query(call.id)
        return
    
    if data == "dedicated_server":
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("🪄 دریافت سرور اختصاصی GROOTZ", url="https://t.me/rezagrootz"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
        )
        bot.edit_message_text("""
🪄 <b>سرور اختصاصی GROOTZ</b>

🌟 با تهیه سرور اختصاصی، از امکانات زیر بهره‌مند شوید:
✅ سرعت بالا و پایداری فوق‌العاده
✅ پشتیبانی VIP ۲۴ ساعته
✅ کانفیگ‌های اختصاصی و شخصی‌سازی شده
✅ بدون محدودیت در ترافیک
✅ ضد فیلتر قوی

📌 <b>برای دریافت سرور اختصاصی، روی دکمه زیر کلیک کنید:</b>
""", call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        bot.answer_callback_query(call.id)
        return
    
    if data == "server_status":
        status_text = """
📊 <b>وضعیت سرورهای GROOTZ</b>
━━━━━━━━━━━━━━━━━━━━━━
🇺🇸 <b>آمریکا:</b> ✅ فعال (پینگ: ۱۵۰ms)
🇩🇪 <b>آلمان:</b> ✅ فعال (پینگ: ۱۲۰ms)
🇳🇱 <b>هلند:</b> ✅ فعال (پینگ: ۱۳۰ms)
🇸🇬 <b>سنگاپور:</b> ✅ فعال (پینگ: ۹۰ms)
🇫🇷 <b>فرانسه:</b> ✅ فعال (پینگ: ۱۴۰ms)
━━━━━━━━━━━━━━━━━━━━━━
🔄 <b>آخرین بروزرسانی:</b> {now}
"""
        bot.edit_message_text(status_text.format(now=datetime.now().strftime("%Y-%m-%d %H:%M")), 
                            call.message.chat.id, call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id)
        return
    
    if data == "profile":
        user = db.get_user(user_id)
        if user:
            config_count = db.get_user_configs(user_id)
            text = f"""
👤 <b>پروفایل شما</b>
━━━━━━━━━━━━━━━━━━━━━━
📛 <b>نام:</b> {user[2]}
🆔 <b>آیدی:</b> <code>{user[0]}</code>
📅 <b>تاریخ عضویت:</b> {datetime.fromtimestamp(user[3]).strftime('%Y-%m-%d')}
📊 <b>تعداد کانفیگ‌ها:</b> {len(config_count)}
💎 <b>وضعیت:</b> {'🌟 ویژه' if user[5] else '🔰 رایگان'}
━━━━━━━━━━━━━━━━━━━━━━
"""
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())
        else:
            bot.edit_message_text("❌ کاربر یافت نشد!", call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id)
        return
    
    if data == "support_bot":
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("❤️ حمایت مالی", url="https://t.me/rezagrootz"),
            InlineKeyboardButton("📢 عضویت در کانال", url="https://t.me/rezagrootz"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
        )
        bot.edit_message_text("""
⭐️ <b>از ربات GROOTZ حمایت کنید!</b>

💎 با حمایت شما، ما می‌توانیم:
• سرورهای بهتری تهیه کنیم
• کانفیگ‌های جدید اضافه کنیم
• پشتیبانی بهتر ارائه دهیم
• ربات را بروزرسانی کنیم

🙏 <b>با یک کلیک، از ما حمایت کنید!</b>
""", call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        bot.answer_callback_query(call.id)
        return
    
    # ========== دریافت کانفیگ ==========
    if data.startswith("config_"):
        country = data.split("_")[1]
        config_map = {
            "usa": PREMIUM_CONFIGS[0],
            "germany": PREMIUM_CONFIGS[1],
            "netherlands": PREMIUM_CONFIGS[2],
            "singapore": PREMIUM_CONFIGS[3],
            "france": PREMIUM_CONFIGS[4]
        }
        config = config_map.get(country)
        if config:
            db.add_config(user_id, config["config"])
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                InlineKeyboardButton("📋 کپی کانفیگ", callback_data=f"copy_{country}"),
                InlineKeyboardButton("🔙 بازگشت", callback_data="free_config")
            )
            bot.edit_message_text(
                f"🌍 <b>کانفیگ {config['name']}</b>\n\n{format_config(config['config'])}\n\n✅ این کانفیگ در پروفایل شما ذخیره شد.",
                call.message.chat.id, call.message.message_id, reply_markup=keyboard
            )
        else:
            bot.answer_callback_query(call.id, "❌ کانفیگ یافت نشد!")
        return
    
    if data.startswith("copy_"):
        country = data.split("_")[1]
        config_map = {
            "usa": PREMIUM_CONFIGS[0],
            "germany": PREMIUM_CONFIGS[1],
            "netherlands": PREMIUM_CONFIGS[2],
            "singapore": PREMIUM_CONFIGS[3],
            "france": PREMIUM_CONFIGS[4]
        }
        config = config_map.get(country)
        if config:
            bot.send_message(call.message.chat.id, f"📋 <b>کانفیگ {config['name']}</b>\n\n<code>{config['config']}</code>", parse_mode='HTML')
            bot.answer_callback_query(call.id, "✅ کانفیگ ارسال شد!")
        return
    
    # ========== کانفیگ‌های ویژه ==========
    if data.startswith("premium_"):
        premium_type = data.split("_")[1]
        premium_map = {
            "gold": "💎 کانفیگ طلایی",
            "diamond": "👑 کانفیگ الماس",
            "platinum": "🌟 کانفیگ پلاتینیوم",
            "custom": "🪄 کانفیگ اختصاصی"
        }
        name = premium_map.get(premium_type, "کانفیگ ویژه")
        # انتخاب یک کانفیگ تصادفی از لیست برای نمایش
        config = random.choice(PREMIUM_CONFIGS)["config"]
        db.add_config(user_id, config)
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("📋 دریافت کانفیگ", callback_data=f"get_premium_{premium_type}"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="premium_config")
        )
        bot.edit_message_text(
            f"{name}\n\n✅ کانفیگ ویژه شما آماده است!\nبرای دریافت روی دکمه کلیک کنید.",
            call.message.chat.id, call.message.message_id, reply_markup=keyboard
        )
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("get_premium_"):
        premium_type = data.split("_")[2]
        config = random.choice(PREMIUM_CONFIGS)["config"]
        bot.send_message(call.message.chat.id, f"💎 <b>کانفیگ ویژه شما</b>\n\n<code>{config}</code>", parse_mode='HTML')
        bot.answer_callback_query(call.id, "✅ کانفیگ ویژه ارسال شد!")
        return
    
    # ========== پنل ادمین ==========
    if data.startswith("admin_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "⛔ شما دسترسی ندارید!")
            return
        
        if data == "admin_stats":
            users = db.get_all_users()
            configs = db.cursor.execute("SELECT COUNT(*) FROM configs").fetchone()[0]
            text = f"""
📊 <b>آمار ربات GROOTZ</b>
━━━━━━━━━━━━━━━━━━━━━━
👥 <b>تعداد کاربران:</b> {len(users)}
📋 <b>تعداد کانفیگ‌ها:</b> {configs}
📅 <b>آخرین بروزرسانی:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━
"""
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel())
            bot.answer_callback_query(call.id)
            return
        
        if data == "admin_broadcast":
            bot.send_message(call.message.chat.id, "📨 <b>ارسال همگانی</b>\n\nلطفاً پیام خود را ارسال کنید. (برای لغو /cancel)")
            bot.answer_callback_query(call.id)
            return
        
        if data == "admin_users":
            users = db.get_all_users()
            if not users:
                bot.edit_message_text("📭 هیچ کاربری یافت نشد!", call.message.chat.id, call.message.message_id)
            else:
                text = "👥 <b>لیست کاربران</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
                for idx, uid in enumerate(users[:20], 1):
                    user = db.get_user(uid)
                    if user:
                        text += f"{idx}. {user[2]} - <code>{uid}</code>\n"
                if len(users) > 20:
                    text += f"\n... و {len(users) - 20} کاربر دیگر"
                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_panel())
            bot.answer_callback_query(call.id)
            return
        
        if data == "admin_settings":
            bot.edit_message_text("⚙️ <b>تنظیمات ادمین</b>\n\n🔧 در حال توسعه...", 
                                call.message.chat.id, call.message.message_id, reply_markup=admin_panel())
            bot.answer_callback_query(call.id)
            return

def back_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 بازگشت", callback_data="back_main"))
    return keyboard

# ==================== دریافت پیام‌ها برای ارسال همگانی ====================
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_broadcast(message: Message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ عملیات لغو شد.")
        return
    
    if is_admin(message.from_user.id) and message.text:
        # ارسال همگانی
        users = db.get_all_users()
        sent = 0
        failed = 0
        for uid in users:
            try:
                bot.send_message(uid, f"📢 <b>پیام همگانی از GROOTZ</b>\n\n{message.text}")
                sent += 1
                time.sleep(0.1)
            except:
                failed += 1
        bot.reply_to(message, f"✅ ارسال شد!\n✓ موفق: {sent}\n✗ ناموفق: {failed}")
        return
    
    # پاسخ به پیام‌های عادی
    if message.text:
        if any(word in message.text.lower() for word in ["سلام", "درود", "hi", "hello"]):
            bot.reply_to(message, "👋 سلام! برای دریافت کانفیگ، روی /start کلیک کنید.")
        elif "کانفیگ" in message.text or "vless" in message.text.lower():
            bot.reply_to(message, "🔗 برای دریافت کانفیگ، از منوی ربات استفاده کنید:\n/start", reply_markup=main_menu())
        else:
            bot.reply_to(message, "🤖 برای اطلاعات بیشتر، لطفاً از دستور /start استفاده کنید.")

# ==================== اجرای ربات ====================
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 ربات فوق‌پیشرفته GROOTZ V2")
    print("=" * 70)
    print(f"👑 ادمین: {ADMIN_IDS}")
    print("💎 قابلیت‌ها:")
    print("  ✅ دریافت کانفیگ V2Ray با کیفیت بالا")
    print("  ✅ سرورهای اختصاصی و پرسرعت")
    print("  ✅ پشتیبانی ۲۴ ساعته")
    print("  ✅ کانفیگ‌های ضد فیلتر و پایدار")
    print("  ✅ کاملاً رایگان و سریع")
    print("=" * 70)
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"❌ خطا: {e}")
            print("🔄 راه‌اندازی مجدد در 5 ثانیه...")
            time.sleep(5)