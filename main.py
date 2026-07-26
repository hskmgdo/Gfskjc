import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import sqlite3
import time
import random
import base64
import json
from datetime import datetime

# ==================== تنظیمات ====================
BOT_TOKEN = "8423981755:AAFaEYzOefEaxDiuyvKKyyTJzlhDXWSqyRw"
ADMIN_IDS = [8916314219]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

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
                join_date INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                config TEXT,
                created_at INTEGER
            )
        ''')
        self.conn.commit()

    def add_user(self, user_id, username, first_name):
        now = int(time.time())
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name, join_date) VALUES (?, ?, ?, ?)",
            (user_id, username, first_name, now)
        )
        self.conn.commit()

    def save_config(self, user_id, config):
        self.cursor.execute(
            "INSERT INTO configs (user_id, config, created_at) VALUES (?, ?, ?)",
            (user_id, config, int(time.time()))
        )
        self.conn.commit()

    def get_configs(self, user_id):
        self.cursor.execute("SELECT config FROM configs WHERE user_id = ? ORDER BY id DESC", (user_id,))
        return self.cursor.fetchall()

db = Database()

# ==================== کانفیگ‌های StormDNS ====================
CONFIGS = [
    {
        "flag": "🇺🇸",
        "name": "آمریکا",
        "color": "🔴",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6ImkuYXJhc2toYXRhcmUuZ2dmZi5uZXQiLCJlbmNyeXB0aW9uX2tleSI6IjY0MTVlYjhmOTBmMWQ0NjY1N2JjZTljYjc5MTg2NDY2IiwiZW5jcnlwdGlvbl9tZXRob2QiOjF9fX0="
    },
    {
        "flag": "🇩🇪",
        "name": "آلمان",
        "color": "🟡",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6ImMuYXJhc2toYXRhcmUxLmdnZmYubmV0IiwiZW5jcnlwdGlvbl9rZXkiOiJkYmYwMmYyYWVmZmQzM2QyNDY0M2ViODM4OGY2N2Y0ZCIsImVuY3J5cHRpb25fbWV0aG9kIjoxfX19"
    },
    {
        "flag": "🇳🇱",
        "name": "هلند",
        "color": "🟠",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6InEuYXJhc2toYXRhcmUuZ2dmZi5uZXQiLCJlbmNyeXB0aW9uX2tleSI6IjFkYjFiMWIyNGM2N2IxNzYwOTAzMmNjNDdhZmRhMzZlIiwiZW5jcnlwdGlvbl9tZXRob2QiOjF9fX0="
    },
    {
        "flag": "🇸🇬",
        "name": "سنگاپور",
        "color": "🔵",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6Im4uYXJhc2toYXRhcmUuZ2dmZi5uZXQiLCJlbmNyeXB0aW9uX2tleSI6IjU4MTcyOTA4ZGFhNTAxZTk0MjUzNWU2NTY3NzkwM2ZkIiwiZW5jcnlwdGlvbl9tZXRob2QiOjF9fX0="
    },
    {
        "flag": "🇫🇷",
        "name": "فرانسه",
        "color": "🟣",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6Imx5LmFyYXNraGF0YXJlLmdnZmYubmV0IiwiZW5jcnlwdGlvbl9rZXkiOiJkMzM4NmM1MzkxZmRmOTJjMmNkODM3YmFkZTBhNGVjYyIsImVuY3J5cHRpb25fbWV0aG9kIjoxfX19"
    },
    {
        "flag": "🇮🇷",
        "name": "ایران",
        "color": "🟢",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6ImlsLmFyYXNraGF0YXJlLmdnZmYubmV0IiwiZW5jcnlwdGlvbl9rZXkiOiJmNzk4MDAyYzlkMTkxMTg4M2MzOTE2YTQ4ZTkzNTVkMiIsImVuY3J5cHRpb25fbWV0aG9kIjoxfX19"
    },
    {
        "flag": "🇨🇦",
        "name": "کانادا",
        "color": "🔵",
        "config": "stormdns://eyJzY2hlbWEiOiJ3aGl0ZWRucy5wcm9maWxlIiwidmVyc2lvbiI6MSwiaW1wb3J0X3R5cGUiOiJzdG9ybWRucyIsInByb2ZpbGUiOnsibmFtZSI6IlJFWkEgR1JPT1RaIiwic2VydmVyIjp7ImRvbWFpbiI6ImlzLmFyYXNraGF0YXJlLmdnZmYubmV0IiwiZW5jcnlwdGlvbl9rZXkiOiI2MmIyNjQ0NzU5MjU4OWE0NmQ1MzdlY2M5NDc3MzY2NiIsImVuY3J5cHRpb25fbWV0aG9kIjoxfX19"
    }
]

# ==================== کیبوردهای رنگی ====================
def main_menu():
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
    
    # 🟥 دکمه‌های قرمز (آمریکا)
    keyboard.add(
        InlineKeyboardButton("🟥🇺🇸 آمریکا", callback_data="config_usa"),
        InlineKeyboardButton("🟧🇩🇪 آلمان", callback_data="config_germany"),
        InlineKeyboardButton("🟨🇳🇱 هلند", callback_data="config_netherlands"),
        InlineKeyboardButton("🟩🇸🇬 سنگاپور", callback_data="config_singapore"),
        InlineKeyboardButton("🟦🇫🇷 فرانسه", callback_data="config_france"),
        InlineKeyboardButton("🟪🇮🇷 ایران", callback_data="config_iran"),
        InlineKeyboardButton("⬛🇨🇦 کانادا", callback_data="config_canada")
    )
    
    keyboard.add(
        InlineKeyboardButton("🎲 کانفیگ تصادفی", callback_data="config_random"),
        InlineKeyboardButton("📋 کانفیگ‌های من", callback_data="my_configs"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
    )
    return keyboard

def back_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 بازگشت", callback_data="back_main"))
    return keyboard

# ==================== دستور /start ====================
@bot.message_handler(commands=['start'])
def start_command(message: Message):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name)
    
    text = """
🌟 <b>به ربات REZA GROOTZ خوش آمدید!</b> 🌟

⚡️ <b>ساخت کانفیگ StormDNS</b>
🔹 <b>7 سرور مختلف</b> با کیفیت بالا
🔹 <b>کاملاً رایگان</b>
🔹 <b>ذخیره کانفیگ‌ها</b>

📌 <b>روش ارسال پیام را انتخاب کنید:</b>
"""
    bot.reply_to(message, text, reply_markup=main_menu())

# ==================== کال‌بک‌ها ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    data = call.data
    
    # ========== انتخاب زبان ==========
    if data.startswith('lang_'):
        lang = data.split('_')[1]
        bot.answer_callback_query(call.id, f"✅ زبان به {lang} تغییر کرد!")
        return
    
    # ========== بازگشت ==========
    if data == "back_main":
        text = """
🌟 <b>به ربات REZA GROOTZ خوش آمدید!</b> 🌟

⚡️ <b>ساخت کانفیگ StormDNS</b>
🔹 <b>7 سرور مختلف</b> با کیفیت بالا
🔹 <b>کاملاً رایگان</b>
🔹 <b>ذخیره کانفیگ‌ها</b>

📌 <b>روش ارسال پیام را انتخاب کنید:</b>
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu())
        bot.answer_callback_query(call.id)
        return
    
    # ========== دکمه‌های اصلی ==========
    if data == "send_normal":
        text = """
🌍 <b>ساخت کانفیگ StormDNS</b>

🔹 <b>سرور مورد نظر خود را انتخاب کنید:</b>

🟥 آمریکا - پرسرعت
🟧 آلمان - پایدار
🟨 هلند - ضد فیلتر
🟩 سنگاپور - کم پینگ
🟦 فرانسه - سریع
🟪 ایران - داخلی
⬛ کانادا - امن
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=config_menu())
        bot.answer_callback_query(call.id)
        return
    
    if data == "send_anonymous":
        bot.answer_callback_query(call.id, "🕵️ حالت ناشناس فعال شد!")
        bot.send_message(call.message.chat.id, "🕵️ شما در حالت ناشناس هستید!\nبرای دریافت کانفیگ، دکمه 'ارسال معمولی' را بزنید.")
        return
    
    if data == "ai_assistant":
        bot.answer_callback_query(call.id, "🤖 هوش مصنوعی در حال راه‌اندازی...")
        bot.send_message(call.message.chat.id, """
🤖 <b>دستیار هوش مصنوعی GROOTZ</b>

سلام! من اینجام تا بهت کمک کنم.

💬 <b>سوالاتت رو بپرس:</b>
• راهنمای کانفیگ‌ها
• رفع مشکلات اتصال
• مشاوره سرور
• هر سوال دیگه

📌 برای پشتیبانی: @rezagrootz
""", parse_mode='HTML')
        return
    
    if data == "prices":
        text = """
💰 <b>قیمت‌های GROOTZ</b>
━━━━━━━━━━━━━━━━━━━━━━
🟥🇺🇸 <b>آمریکا:</b> رایگان
🟧🇩🇪 <b>آلمان:</b> رایگان
🟨🇳🇱 <b>هلند:</b> رایگان
🟩🇸🇬 <b>سنگاپور:</b> رایگان
🟦🇫🇷 <b>فرانسه:</b> رایگان
🟪🇮🇷 <b>ایران:</b> رایگان
⬛🇨🇦 <b>کانادا:</b> رایگان
━━━━━━━━━━━━━━━━━━━━━━
💎 <b>همه سرورها کاملاً رایگان هستند!</b>

📌 <b>ویژگی‌ها:</b>
✅ سرعت بالا
✅ پایداری فوق‌العاده
✅ ضد فیلتر قوی
✅ پشتیبانی ۲۴ ساعته
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())
        bot.answer_callback_query(call.id)
        return
    
    if data == "make_qr":
        bot.answer_callback_query(call.id, "📱 در حال ساخت QR...")
        bot.send_message(call.message.chat.id, """
📱 <b>ساخت QR Code</b>

لطفاً کانفیگ خود را به همراه پیام بفرستید تا QR بسازم.

مثال:
🔹 کانفیگ: stormdns://...
🔹 توضیحات: کانفیگ آمریکا

📌 بعد از دریافت، QR ساخته می‌شود.
""", parse_mode='HTML')
        return
    
    # ========== ساخت کانفیگ ==========
    if data.startswith('config_'):
        server = data.split('_')[1]
        config_map = {
            'usa': 0, 'germany': 1, 'netherlands': 2,
            'singapore': 3, 'france': 4, 'iran': 5, 'canada': 6
        }
        index = config_map.get(server, 0)
        config = CONFIGS[index]
        
        # ذخیره در دیتابیس
        db.save_config(call.from_user.id, config['config'])
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("📋 کپی کانفیگ", callback_data=f"copy_{server}"),
            InlineKeyboardButton("🔄 کانفیگ جدید", callback_data="send_normal"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
        )
        
        text = f"""
{config['color']}{config['flag']} <b>کانفیگ {config['name']}</b>
━━━━━━━━━━━━━━━━━━━━━━
<code>{config['config']}</code>
━━━━━━━━━━━━━━━━━━━━━━
✅ کانفیگ شما با موفقیت ساخته شد!
📋 برای کپی کردن روی دکمه کلیک کنید.

💡 <b>نکته:</b> این کانفیگ در لیست کانفیگ‌های شما ذخیره شد.
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        bot.answer_callback_query(call.id, "✅ کانفیگ ساخته شد!")
        return
    
    # ========== کانفیگ تصادفی ==========
    if data == 'config_random':
        config = random.choice(CONFIGS)
        db.save_config(call.from_user.id, config['config'])
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("📋 کپی کانفیگ", callback_data="copy_random"),
            InlineKeyboardButton("🎲 دوباره تصادفی", callback_data="config_random"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
        )
        
        text = f"""
🎲 <b>کانفیگ تصادفی</b>
━━━━━━━━━━━━━━━━━━━━━━
{config['color']}{config['flag']} <b>{config['name']}</b>
<code>{config['config']}</code>
━━━━━━━━━━━━━━━━━━━━━━
✅ کانفیگ تصادفی با موفقیت ساخته شد!
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
        bot.answer_callback_query(call.id, "🎲 کانفیگ تصادفی!")
        return
    
    # ========== کپی کانفیگ ==========
    if data.startswith('copy_'):
        server = data.split('_')[1]
        config_map = {
            'usa': 0, 'germany': 1, 'netherlands': 2,
            'singapore': 3, 'france': 4, 'iran': 5, 'canada': 6
        }
        
        if server == 'random':
            config = random.choice(CONFIGS)
        else:
            index = config_map.get(server, 0)
            config = CONFIGS[index]
        
        bot.send_message(
            call.message.chat.id,
            f"📋 <b>کانفیگ {config['name']}</b>\n\n<code>{config['config']}</code>",
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id, "✅ کانفیگ کپی شد!")
        return
    
    # ========== کانفیگ‌های من ==========
    if data == "my_configs":
        configs = db.get_configs(call.from_user.id)
        
        if not configs:
            text = "❌ شما هنوز کانفیگی نساخته‌اید!\nاز دکمه 'ارسال معمولی' استفاده کنید."
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_button())
            bot.answer_callback_query(call.id, "❌ کانفیگی وجود ندارد!")
            return
        
        text = "📋 <b>کانفیگ‌های شما</b>\n━━━━━━━━━━━━━━━━━━━━━━\n"
        for i, cfg in enumerate(configs[:10], 1):
            config_text = cfg[0][:50] + "..." if len(cfg[0]) > 50 else cfg[0]
            text += f"{i}. <code>{config_text}</code>\n"
        
        if len(configs) > 10:
            text += f"\n... و {len(configs) - 10} کانفیگ دیگر"
        
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("🗑️ پاک کردن همه", callback_data="clear_configs"),
            InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
        )
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=keyboard, parse_mode='HTML')
        bot.answer_callback_query(call.id)
        return
    
    if data == "clear_configs":
        db.cursor.execute("DELETE FROM configs WHERE user_id = ?", (call.from_user.id,))
        db.conn.commit()
        bot.answer_callback_query(call.id, "✅ همه کانفیگ‌ها پاک شدند!")
        bot.edit_message_text(
            "🗑️ همه کانفیگ‌های شما پاک شدند.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=back_button()
        )

# ==================== اجرا ====================
if __name__ == "__main__":
    print("=" * 70)
    print("🌟 ربات StormDNS GROOTZ (دکمه‌های رنگی)")
    print("=" * 70)
    print("👑 ادمین: @rezagrootz")
    print("💎 قابلیت‌ها:")
    print("  ✅ دکمه‌های رنگی با ایموجی (🟥🟧🟨🟩🟦🟪⬛)")
    print("  ✅ 7 سرور مختلف")
    print("  ✅ کانفیگ تصادفی")
    print("  ✅ ذخیره کانفیگ‌ها")
    print("  ✅ ارسال ناشناس")
    print("  ✅ هوش مصنوعی")
    print("=" * 70)
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            print(f"❌ خطا: {e}")
            time.sleep(5)
