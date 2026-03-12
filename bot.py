import os, asyncio, re, glob, threading, random
from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import SessionPasswordNeededError, FloodWaitError
from flask import Flask

# --- [ نظام الحماية واستمرارية الخدمة ] ---
app = Flask('')
@app.route('/')
def home(): return "V10 PRO IS ONLINE"
def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# --- [ البيانات الأساسية ] ---
API_ID = 25880715
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'
ADMIN_ID = 7515408355

bot = TelegramClient('v10_master', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- [ واجهة الأزرار المطورة ] ---
MAIN_MENU = [
    [Button.text("🔥 هجوم شامل", resize=True), Button.text("➕ إضافة حساب", resize=True)],
    [Button.text("🔍 فحص الجلسات", resize=True), Button.text("📊 الإحصائيات", resize=True)],
    [Button.text("🛠️ الإعدادات", resize=True)]
]

# أنواع البلاغات القوية
REPORT_TYPES = {
    "Spam": types.InputReportReasonSpam(),
    "Violence": types.InputReportReasonViolence(),
    "Pornography": types.InputReportReasonPornography(),
    "Fake Account": types.InputReportReasonFake(),
    "Child Abuse": types.InputReportReasonChildAbuse()
}

# --- [ معالجة الأوامر ] ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(f"🚀 **مرحباً بك يا سالم في V10 PRO**\n\nهذه النسخة مطورة لمحاكاة الهجمات الجماعية وإدارة الحسابات بكفاءة عالية.", buttons=MAIN_MENU)

@bot.on(events.NewMessage(func=lambda e: e.text == "📊 الإحصائيات"))
async def stats(event):
    sessions = glob.glob('user_sessions/*.session')
    await event.respond(f"📈 **إحصائيات الأسطول:**\n\n📦 عدد الحسابات: `{len(sessions)}`\n📡 حالة الاتصال: مستقر ✅\n🛡️ نظام الحماية: نشط 🛡️")

@bot.on(events.NewMessage(func=lambda e: e.text == "➕ إضافة حساب"))
async def add_acc(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("📱 أرسل الرقم مع رمز الدولة (مثال: +218...):")
        phone = (await conv.get_response()).text.strip().replace(" ", "")
        client = TelegramClient(f'user_sessions/{phone}', API_ID, API_HASH)
        await client.connect()
        try:
            req = await client.send_code_request(phone)
            await conv.send_message("📩 **حول (Forward)** رسالة الكود هنا:")
            msg = await conv.get_response()
            otp = re.search(r'\b\d{5}\b', msg.text)
            if otp:
                try:
                    await client.sign_in(phone, otp.group(0), phone_code_hash=req.phone_code_hash)
                    await conv.send_message("✅ تم إضافة الحساب للأسطول!")
                except SessionPasswordNeededError:
                    await conv.send_message("🔐 أرسل كلمة سر التحقق بخطوتين:")
                    await client.sign_in(password=(await conv.get_response()).text)
                    await conv.send_message("✅ تم التحقق والربط!")
            else: await conv.send_message("❌ كود خاطئ.")
        except Exception as e: await conv.send_message(f"❌ خطأ: {e}")
        await client.disconnect()

@bot.on(events.NewMessage(func=lambda e: e.text == "🔥 هجوم شامل"))
async def attack(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("🔗 أرسل رابط الرسالة أو الحساب المستهدف:")
        target = (await conv.get_response()).text
        
        btns = [[Button.inline(name, data=f"atk_{name}_{target}")] for name in REPORT_TYPES.keys()]
        await conv.send_message("⚠️ اختر نوع الهجوم المكثف:", buttons=btns)

@bot.on(events.CallbackQuery(pattern=r"atk_(.*)_(.*)"))
async def start_attack(event):
    reason_str = event.data_decode.split('_')[1]
    target = event.data_decode.split('_')[2]
    reason = REPORT_TYPES[reason_str]
    
    await event.edit(f"🔥 جاري شن هجوم ({reason_str}) من جميع الحسابات...")
    
    sessions = glob.glob('user_sessions/*.session')
    success = 0
    for s in sessions:
        cli = TelegramClient(s, API_ID, API_HASH)
        try:
            await cli.connect()
            # استخراج المعرف والمعرف الرقمي من الرابط
            parts = target.split('/')
            await cli(functions.messages.ReportRequest(peer=parts[-2], id=[int(parts[-1])], reason=reason))
            success += 1
            await cli.disconnect()
            await asyncio.sleep(random.randint(2, 5)) # حماية من الحظر
        except Exception: continue
    
    await event.respond(f"✅ انتهى الهجوم الشامل.\n🚀 تم إرسال `{success}` بلاغ بنجاح!")

# تشغيل النظام
if not os.path.exists('user_sessions'): os.makedirs('user_sessions')
print("--- [ V10 PRO IS LIVE ] ---")
bot.run_until_disconnected()
