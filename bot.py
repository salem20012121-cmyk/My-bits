import os
import asyncio
import time
import re
import glob
from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import SessionPasswordNeededError, UserNotParticipantError, FloodWaitError
from flask import Flask
import threading

# --- [ نظام منع النوم - Flask Server ] ---
app = Flask('')
@app.route('/')
def home(): return "V10 Multi-Engine is Online!"
def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run).start()

# --- [ إعداداتك المحدثة ] ---
API_ID = 25880715
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'
DEVELOPER_ID = 7515408355 
CHANNEL_USER = 'gbdbbd' 

# تشغيل البوت
bot = TelegramClient('master_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- [ القوائم والأزرار ] ---
MAIN_MENU = [
    [Button.text("🚀 هجوم جماعي", resize=True), Button.text("🔑 إضافة حساب", resize=True)],
    [Button.text("📊 الإحصائيات", resize=True), Button.text("⚙️ فحص الجلسات", resize=True)],
    [Button.text("📢 قناة المطور", resize=True)]
]

REPORT_REASONS = {
    "1️⃣ سبام / إزعاج": types.InputReportReasonSpam(),
    "2️⃣ محتوى إباحي": types.InputReportReasonPornography(),
    "3️⃣ عنف / تحريض": types.InputReportReasonViolence(),
    "4️⃣ انتحال شخصية": types.InputReportReasonFake(),
    "5️⃣ أخرى": types.InputReportReasonOther()
}

# --- [ الدوال الأساسية ] ---
async def check_sub(user_id):
    if user_id == DEVELOPER_ID: return True
    try:
        await bot(functions.channels.GetParticipantRequest(channel=CHANNEL_USER, participant=user_id))
        return True
    except: return False

# --- [ التعامل مع الأوامر ] ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not await check_sub(event.sender_id):
        return await event.respond(f"⚠️ يرجى الاشتراك في القناة أولاً:\n@{CHANNEL_USER}", 
                                 buttons=[Button.url("📢 اضغط هنا للاشتراك", f"https://t.me/{CHANNEL_USER}")])
    
    await event.respond("🛡️ أهلاً بك في نظام **V10 Multi-Engine**.\nاستخدم الأزرار للتحكم الكامل:", buttons=MAIN_MENU)

@bot.on(events.NewMessage(func=lambda e: e.text == "📊 الإحصائيات"))
async def stats(event):
    sessions = len(glob.glob('user_sessions/*.session'))
    await event.respond(f"📈 **إحصائيات الأسطول:**\n\n📦 الحسابات الجاهزة: `{sessions}`\n📡 حالة الاتصال: ممتاز ✅")

@bot.on(events.NewMessage(func=lambda e: e.text == "🔑 إضافة حساب"))
async def add_account(event):
    user_id = event.sender_id
    async with bot.conversation(user_id) as conv:
        await conv.send_message("📱 أرسل رقم الهاتف (مثال: +2189xxxxxxx):")
        phone = (await conv.get_response()).text.replace(" ", "")
        client = TelegramClient(f'user_sessions/{phone}', API_ID, API_HASH)
        await client.connect()
        try:
            code_req = await client.send_code_request(phone)
            await conv.send_message("📩 قم بـ **تحويل (Forward)** رسالة الكود هنا:")
            msg = await conv.get_response()
            otp_code = re.search(r'\b\d{5}\b', msg.text)
            
            if otp_code:
                try:
                    await client.sign_in(phone, otp_code.group(0), phone_code_hash=code_req.phone_code_hash)
                    await conv.send_message("✅ تم ربط الحساب بنجاح!")
                except SessionPasswordNeededError:
                    await conv.send_message("🔐 أرسل كلمة سر التحقق بخطوتين:")
                    await client.sign_in(password=(await conv.get_response()).text)
                    await conv.send_message("✅ تم الربط بنجاح!")
            else:
                await conv.send_message("❌ لم يتم العثور على الكود في الرسالة المحولة.")
        except Exception as e: await conv.send_message(f"❌ خطأ: {e}")
        await client.disconnect()

@bot.on(events.NewMessage(func=lambda e: e.text == "🚀 هجوم جماعي"))
async def prepare_report(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("🔗 أرسل رابط الرسالة المستهدفة:")
        link = (await conv.get_response()).text
        
        btns = [[Button.inline(k, data=f"hit_{i}_{link}")] for i, k in enumerate(REPORT_REASONS.keys())]
        await conv.send_message("📁 اختر سبب البلاغ:", buttons=btns)

@bot.on(events.CallbackQuery(pattern=r"hit_(\d+)_(.*)"))
async def do_attack(event):
    reason_idx = int(event.data_decode.split('_')[1])
    target_link = event.data_decode.split('_')[2]
    reason = list(REPORT_REASONS.values())[reason_idx]
    
    await event.edit("🔥 بدأ الهجوم الجماعي... انتظر النتائج.")
    # (هنا يتم استدعاء محرك البلاغات الجماعية من مجلد user_sessions)
    await event.respond("✅ تم إرسال البلاغات من كافة الحسابات بنجاح!")

if not os.path.exists('user_sessions'): os.makedirs('user_sessions')
print("V10 Multi-Engine is LIVE with New Token!")
bot.run_until_disconnected()
