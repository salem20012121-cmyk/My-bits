import os, asyncio, time, re, glob, threading
from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import SessionPasswordNeededError, UserNotParticipantError, FloodWaitError
from flask import Flask

# --- [ نظام الحماية ومنع النوم ] ---
app = Flask('')
@app.route('/')
def home(): return "V10 Engine is Alive!"
def run(): app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run, daemon=True).start()

# --- [ البيانات الأساسية ] ---
API_ID = 25880715
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'
DEVELOPER_ID = 7515408355 
CHANNEL_USER = 'gbdbbd' 

bot = TelegramClient('master_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- [ الكيبوردات ] ---
MAIN_MENU = [
    [Button.text("🚀 هجوم جماعي", resize=True), Button.text("🔑 إضافة حساب", resize=True)],
    [Button.text("📊 الإحصائيات", resize=True), Button.text("⚙️ فحص الجلسات", resize=True)],
    [Button.text("📢 قناة المطور", resize=True)]
]

REPORT_REASONS = {
    "1️⃣ سبام": types.InputReportReasonSpam(),
    "2️⃣ إباحي": types.InputReportReasonPornography(),
    "3️⃣ عنف": types.InputReportReasonViolence(),
    "4️⃣ انتحال": types.InputReportReasonFake(),
    "5️⃣ أخرى": types.InputReportReasonOther()
}

# --- [ الدوال ] ---
async def check_sub(user_id):
    if user_id == DEVELOPER_ID: return True
    try:
        await bot(functions.channels.GetParticipantRequest(channel=CHANNEL_USER, participant=user_id))
        return True
    except: return False

# --- [ معالجة الأوامر ] ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not await check_sub(event.sender_id):
        return await event.respond(f"⚠️ اشترك في القناة أولاً: @{CHANNEL_USER}", 
                                 buttons=[Button.url("📢 اضغط هنا", f"https://t.me/{CHANNEL_USER}")])
    await event.respond("🛡️ **V10 Multi-Engine** جاهز للعمل يا سالم.", buttons=MAIN_MENU)

@bot.on(events.NewMessage(func=lambda e: e.text == "📊 الإحصائيات"))
async def stats(event):
    sessions = len(glob.glob('user_sessions/*.session'))
    await event.respond(f"📈 الحسابات المتصلة: `{sessions}`\n📡 السيرفر: مستقر ✅")

@bot.on(events.NewMessage(func=lambda e: e.text == "🔑 إضافة حساب"))
async def add_account(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("📱 أرسل رقم الهاتف (مثال: +2189xxxxxxxx):")
        phone = (await conv.get_response()).text.replace(" ", "")
        client = TelegramClient(f'user_sessions/{phone}', API_ID, API_HASH)
        await client.connect()
        try:
            code_req = await client.send_code_request(phone)
            await conv.send_message("📩 **حول (Forward)** رسالة الكود إلى هنا الآن:")
            msg = await conv.get_response()
            otp_code = re.search(r'\b\d{5}\b', msg.text)
            if otp_code:
                try:
                    await client.sign_in(phone, otp_code.group(0), phone_code_hash=code_req.phone_code_hash)
                    await conv.send_message("✅ تم إضافة الحساب بنجاح!")
                except SessionPasswordNeededError:
                    await conv.send_message("🔐 أرسل كلمة سر التحقق بخطوتين:")
                    await client.sign_in(password=(await conv.get_response()).text)
                    await conv.send_message("✅ تم الربط!")
            else: await conv.send_message("❌ فشل استخراج الكود.")
        except Exception as e: await conv.send_message(f"❌ خطأ: {e}")
        await client.disconnect()

@bot.on(events.NewMessage(func=lambda e: e.text == "🚀 هجوم جماعي"))
async def prepare_report(event):
    async with bot.conversation(event.sender_id) as conv:
        await conv.send_message("🔗 أرسل رابط الرسالة المستهدفة:")
        link = (await conv.get_response()).text
        if "t.me/" not in link: return await conv.send_message("❌ الرابط غير صحيح.")
        
        btns = [[Button.inline(k, data=f"h_{i}")] for i, k in enumerate(REPORT_REASONS.keys())]
        await conv.send_message("📁 اختر سبب البلاغ القوي:", buttons=btns)
        # سيتم تخزين الرابط مؤقتاً في هذه الجلسة
        os.environ[f"target_{event.sender_id}"] = link

@bot.on(events.CallbackQuery(pattern=r"h_(\d+)"))
async def do_attack(event):
    reason_idx = int(event.data.decode().split('_')[1])
    reason = list(REPORT_REASONS.values())[reason_idx]
    link = os.environ.get(f"target_{event.sender_id}")
    
    await event.edit("🔥 بدأ الهجوم الجماعي الشامل... يرجى الانتظار.")
    
    session_files = glob.glob('user_sessions/*.session')
    success = 0
    for s in session_files:
        c = TelegramClient(s, API_ID, API_HASH)
        try:
            await c.connect()
            parts = link.split('/')
            await c(functions.messages.ReportRequest(peer=parts[-2], id=[int(parts[-1])], reason=reason))
            success += 1
            await c.disconnect()
        except: continue
    
    await event.respond(f"✅ تم الانتهاء! عدد البلاغات المرسلة: `{success}`")

if not os.path.exists('user_sessions'): os.makedirs('user_sessions')
print("V10 IS READY TO GO!")
bot.run_until_disconnected()
