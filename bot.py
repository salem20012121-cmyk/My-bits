import os
import asyncio
import re
import glob
import threading
from telethon import TelegramClient, events, Button, functions, types
from flask import Flask

# --- [ سيرفر ويب بسيط لمنع Render من إيقاف البوت ] ---
app = Flask('')
@app.route('/')
def home(): return "V10 Engine is Running!"
def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run, daemon=True).start()

# --- [ إعداداتك الرسمية ] ---
API_ID = 25880715
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'
DEVELOPER_ID = 7515408355 
CHANNEL_USER = 'gbdbbd' 

# تشغيل البوت
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# أزرار الكيبورد الثابتة
MAIN_MENU = [
    [Button.text("🚀 هجوم جماعي", resize=True), Button.text("🔑 إضافة حساب", resize=True)],
    [Button.text("📊 الإحصائيات", resize=True), Button.text("⚙️ فحص الجلسات", resize=True)],
    [Button.text("📢 قناة المطور", resize=True)]
]

# أنواع البلاغات
REPORT_REASONS = {
    "1️⃣ سبام / إزعاج": types.InputReportReasonSpam(),
    "2️⃣ محتوى إباحي": types.InputReportReasonPornography(),
    "3️⃣ عنف / تحريض": types.InputReportReasonViolence(),
    "4️⃣ انتحال شخصية": types.InputReportReasonFake(),
    "5️⃣ أخرى": types.InputReportReasonOther()
}

# --- [ دوال التحقق ] ---
async def check_sub(user_id):
    if user_id == DEVELOPER_ID: return True
    try:
        await bot(functions.channels.GetParticipantRequest(channel=CHANNEL_USER, participant=user_id))
        return True
    except: return False

# --- [ معالجة الرسائل ] ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not await check_sub(event.sender_id):
        return await event.respond(f"⚠️ يرجى الاشتراك في قناة البوت أولاً:\n@{CHANNEL_USER}", 
                                 buttons=[Button.url("📢 اضغط هنا للاشتراك", f"https://t.me/{CHANNEL_USER}")])
    await event.respond(f"🛡️ أهلاً بك يا سالم في نظام **V10 Multi-Engine**.\nالبوت يعمل الآن بنجاح على Render!", buttons=MAIN_MENU)

@bot.on(events.NewMessage(func=lambda e: e.text == "📊 الإحصائيات"))
async def stats(event):
    sessions = len(glob.glob('user_sessions/*.session'))
    await event.respond(f"📈 **إحصائيات النظام:**\n\n📦 الحسابات المتاحة للهجوم: `{sessions}`\n📡 حالة السيرفر: متصل ✅")

@bot.on(events.NewMessage(func=lambda e: e.text == "🔑 إضافة حساب"))
async def add_account(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("📱 أرسل رقم الهاتف (مثال: +2189xxxxxxx):")
        phone = (await conv.get_response()).text.strip().replace(" ", "")
        client = TelegramClient(f'user_sessions/{phone}', API_ID, API_HASH)
        await client.connect()
        try:
            code_req = await client.send_code_request(phone)
            await conv.send_message("📩 **حول (Forward)** رسالة كود التحقق من تيليجرام هنا:")
            msg = await conv.get_response()
            otp_code = re.search(r'\b\d{5}\b', msg.text)
            if otp_code:
                try:
                    await client.sign_in(phone, otp_code.group(0), phone_code_hash=code_req.phone_code_hash)
                    await conv.send_message("✅ تم ربط الحساب بنجاح وإضافته للأسطول!")
                except:
                    await conv.send_message("❌ حدث خطأ أثناء التسجيل، تأكد من الكود أو كلمة السر.")
            else:
                await conv.send_message("❌ لم أجد الكود في الرسالة المحولة.")
        except Exception as e:
            await conv.send_message(f"❌ خطأ: {e}")
        await client.disconnect()

@bot.on(events.NewMessage(func=lambda e: e.text == "🚀 هجوم جماعي"))
async def prepare_report(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("🔗 أرسل رابط الرسالة المستهدفة:")
        link = (await conv.get_response()).text
        if "t.me/" not in link:
            return await conv.send_message("❌ الرابط غير صحيح.")
        
        btns = [[Button.inline(k, data=f"r_{i}_{link[-10:]}")] for i, k in enumerate(REPORT_REASONS.keys())]
        await conv.send_message("📁 اختر نوع البلاغ القوي:", buttons=btns)

# إنشاء مجلد الجلسات إذا لم يكن موجوداً
if not os.path.exists('user_sessions'):
    os.makedirs('user_sessions')

print("--- [ V10 IS NOW LIVE ] ---")
bot.run_until_disconnected()
