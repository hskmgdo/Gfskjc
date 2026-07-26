import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "8423981755:AAFaEYzOefEaxDiuyvKKyyTJzlhDXWSqyRw"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode='HTML')

# دکمه‌های رنگی 🌈
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # دکمه‌های زبان با رنگ‌های مختلف
    keyboard.add(
        InlineKeyboardButton("🇺🇸 🔵 English", callback_data="lang_en"),
        InlineKeyboardButton("🇮🇷 🔴 فارسی", callback_data="lang_fa"),
        InlineKeyboardButton("🇩🇪 🟡 Deutsch", callback_data="lang_de"),
        InlineKeyboardButton("🇷🇺 🟣 Русский", callback_data="lang_ru")
    )
    
    # دکمه‌های اصلی با رنگ‌های مختلف
    keyboard.add(
        InlineKeyboardButton("📨 🟩 ارسال معمولی", callback_data="send_normal"),
        InlineKeyboardButton("🕵️ ⬛️ ارسال ناشناس", callback_data="send_anonymous"),
        InlineKeyboardButton("🤖 🟪 هوش مصنوعی", callback_data="ai_assistant"),
        InlineKeyboardButton("💰 🟨 قیمت‌ها", callback_data="prices"),
        InlineKeyboardButton("📱 🟦 ساخت QR", callback_data="make_qr")
    )
    return keyboard

def config_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # دکمه‌های سرور با رنگ‌های مختلف 🎨
    keyboard.add(
        InlineKeyboardButton("🔴🇺🇸 آمریکا", callback_data="config_usa"),
        InlineKeyboardButton("🟠🇩🇪 آلمان", callback_data="config_germany"),
        InlineKeyboardButton("🟡🇳🇱 هلند", callback_data="config_netherlands"),
        InlineKeyboardButton("🟢🇸🇬 سنگاپور", callback_data="config_singapore"),
        InlineKeyboardButton("🔵🇫🇷 فرانسه", callback_data="config_france"),
        InlineKeyboardButton("🟣🇮🇷 ایران", callback_data="config_iran"),
        InlineKeyboardButton("⚫🇨🇦 کانادا", callback_data="config_canada")
    )
    
    keyboard.add(
        InlineKeyboardButton("🎲 کانفیگ تصادفی", callback_data="config_random"),
        InlineKeyboardButton("📋 کانفیگ‌های من", callback_data="my_configs"),
        InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")
    )
    return keyboard

@bot.message_handler(commands=['start'])
def start_command(message):
    text = """
🌟 <b>به ربات REZA GROOTZ خوش آمدید!</b> 🌟

⚡️ <b>ساخت کانفیگ StormDNS</b>
🔹 <b>7 سرور مختلف</b> با کیفیت بالا
🔹 <b>کاملاً رایگان</b>

📌 <b>روش ارسال پیام را انتخاب کنید:</b>
"""
    bot.reply_to(message, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data
    
    if data == "send_normal":
        text = "🌍 <b>سرور مورد نظر خود را انتخاب کنید:</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=config_menu())
        bot.answer_callback_query(call.id)
        return
    
    if data == "back_main":
        text = "🌟 <b>منوی اصلی</b>"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=main_menu())
        bot.answer_callback_query(call.id)
        return
    
    if data.startswith("config_"):
        server = data.split("_")[1]
        bot.answer_callback_query(call.id, f"✅ کانفیگ {server} ساخته شد!")
        bot.send_message(call.message.chat.id, f"📋 کانفیگ شما:\n<code>stormdns://...</code>", parse_mode='HTML')
        return

if __name__ == "__main__":
    print("🚀 ربات با دکمه‌های رنگی اجرا شد!")
    bot.polling()
