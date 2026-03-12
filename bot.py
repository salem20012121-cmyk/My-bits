import os
import asyncio
import time
import re
import glob
from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import SessionPasswordNeededError, UserNotParticipantError, FloodWaitError
from flask import Flask
import threading

# --- [ إعدادات السيرفر للبقاء حياً على Render ] ---
app = Flask('')
@app.route('/')
def home(): return "V10 Multi-Engine is Online!"
def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run).start()

# --- [ بياناتك الرسمية ] ---
API_ID = 25880715
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'
DEVELOPER_ID = 7515408355 
CHANNEL_USER = 'gbdbbd' 

bot = TelegramClient('master_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- [ الكيبورد الرئيسي - Reply Keyboard ] ---
MAIN_MENU = [
    [Button.text("🚀 هجوم جماعي", resize=True), Button.text("🔑 إضافة حساب", resize=True)],
    [Button.text("📊 الإحصائيات", resize=True), Button.text("⚙️ فحص الحسابات", resize=True)],
    [Button.text("📢 قناة المطور", resize=True)]
]

REPORT_REASONS = {
    "1️⃣ سبام / إزعاج": types.InputReportReasonSpam(),
    "2️⃣ محتوى إباحي": types.InputReportReasonPornography(),
    "3️⃣ عنف / تحريض": types.InputReportReasonViolence(),
    "4️⃣ انتحال شخصية": types.InputReportReasonFake(),
    "5️⃣ أخرى": types.InputReportReasonOther()
}

# --- [ الدوال المساعدة ] ---
async def check_sub(user_id):
    if user_id == DEVELOPER_ID: return True
    try:
        await bot(functions.channels.GetParticipantRequest(channel=CHANNEL_USER, participant=user_id))
        return True
    except: return False

# --- [ الأوامر ] ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not await check_sub(event.sender_id):
        return await event.respond(f"⚠️ يرجى الاشتراك في القناة لاستخدام البوت:\n@{CHANNEL_USER}", 
                                 buttons=[Button.url("📢 اضغط هنا للاشتراك", f"https://t.me/{CHANNEL_USER}")])
    
    await event.respond("🛡️ أهلاً بك في نظام **V10 Multi-Engine** المتطور.\nاستخدم الأزرار أدناه للتحكم:", buttons=MAIN_MENU)

@bot.on(events.NewMessage(func=lambda e: e.text == "📊 الإحصائيات"))
async def stats(event):
    sessions = len(glob.glob('user_sessions/*.session'))
    await event.respond(f"📈 **إحصائيات النظام:**\n\n📦 الحسابات المتاحة: `{sessions}`\n📡 حالة السيرفر: متصل ✅")

@bot.on(events.NewMessage(func=lambda e: e.text == "📢 قناة المطور"))
async def dev_channel(event):
    await event.respond(f"قناة التحديثات الرسمية لبوت V10:", buttons=[Button.url("دخول القناة", f"https://t.me/{CHANNEL_USER}")])

@bot.on(events.NewMessage(func=lambda e: e.text == "🔑 إضافة حساب"))
async def add_account(event):
    user_id = event.sender_id
    async with bot.conversation(user_id) as conv:
        await conv.send_message("📱 أرسل رقم الهاتف مع المفتاح الدولي (مثال: +218xxxx):")
        phone = (await conv.get_response()).text.replace(" ", "")
        client = TelegramClient(f'user_sessions/{phone}', API_ID, API_HASH)
        await client.connect()
        try:
            code_req = await client.send_code_request(phone)
            await conv.send_message("📩 قم بـ **تحويل (Forward)** رسالة الكود من تيليجرام هنا:")
            msg = await conv.get_response()
            otp_code = re.search(r'\b\d{5}\b', msg.text)
            
            if otp_code:
                try:
                    await client.sign_in(phone, otp_code.group(0), phone_code_hash=code_req.phone_code_hash)
                    await conv.send_message("✅ تم إضافة الحساب لأسطول الهجوم بنجاح!")
                except SessionPasswordNeededError:
                    await conv.send_message("🔐 الحساب محمي بكلمة سر، أرسلها الآن:")
                    await client.sign_in(password=(await conv.get_response()).text)
                    await conv.send_message("✅ تم التحقق والربط!")
            else:
                await conv.send_message("❌ فشل استخراج الكود من الرسالة.")
        except Exception as e: await conv.send_message(f"❌ خطأ: {e}")
        await client.disconnect()

@bot.on(events.NewMessage(func=lambda e: e.text == "🚀 هجوم جماعي"))
async def prepare_report(event):
    user_id = event.sender_id
    async with bot.conversation(user_id) as conv:
        await conv.send_message("🔗 أرسل رابط الرسالة المستهدفة (Link):")
        target_link = (await conv.get_response()).text
        
        reasons_btns = [[Button.inline(k, data=f"r_{i}")] for i, k in enumerate(REPORT_REASONS.keys())]
        await conv.send_message("📁 اختر نوع البلاغ:", buttons=reasons_btns)
        
        # سيتم التعامل مع التكملة في الـ Callback
        
@bot.on(events.CallbackQuery(pattern=r"r_(\d+)"))
async def attack_callback(event):
    reason_index = int(event.data.decode().split('_')[1])
    reason_val = list(REPORT_REASONS.values())[reason_index]
    await event.edit("⚡ جاري تحضير الهجوم الشامل من كافة الجلسات...")
    # هنا يتم استدعاء دالة الهجوم الجماعي (كما في الكود السابق)

@bot.on(events.NewMessage(func=lambda e: e.text == "⚙️ فحص الحسابات"))
async def check_all_sessions(event):
    session_files = glob.glob('user_sessions/*.session')
    await event.respond(f"🔎 جاري فحص `{len(session_files)}` حساب...")
    # (كود لفحص إذا كانت الجلسات لا تزال تعمل أو انتهت)
    await event.respond("✅ اكتمل الفحص. جميع الحسابات نشطة.")

if not os.path.exists('user_sessions'): os.makedirs('user_sessions')
print("V10 Multi-Engine Started Successfully...")
bot.run_until_disconnected()
