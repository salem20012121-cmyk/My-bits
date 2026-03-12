import os, asyncio, threading, re, glob
from telethon import TelegramClient, events, Button, functions, types
from flask import Flask

# --- [ سيرفر الويب لمنع Render من النوم ] ---
app = Flask('')
@app.route('/')
def home(): return "V10 Engine is Online"
def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- [ إعداداتك الرسمية ] ---
API_ID = 25880715
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'
DEVELOPER_ID = 7515408355
CHANNEL_USER = 'gbdbbd'

bot = TelegramClient('bot_session', API_ID, API_HASH)

# الأزرار الرئيسية
MAIN_MENU = [
    [Button.text("🚀 هجوم جماعي", resize=True), Button.text("🔑 إضافة حساب", resize=True)],
    [Button.text("📊 الإحصائيات", resize=True), Button.text("📢 قناة المطور", resize=True)]
]

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(f"🛡️ **V10 Multi-Engine** جاهز للعمل يا سالم.\nاستخدم الأزرار أدناه للتحكم:", buttons=MAIN_MENU)

@bot.on(events.NewMessage(func=lambda e: e.text == "📊 الإحصائيات"))
async def stats(event):
    count = len(glob.glob('user_sessions/*.session'))
    await event.respond(f"📈 الحسابات المتاحة: `{count}`\n📡 السيرفر: مستقر ✅")

async def main():
    if not os.path.exists('user_sessions'): os.makedirs('user_sessions')
    print("--- [ البوت بدأ العمل الآن ] ---")
    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
