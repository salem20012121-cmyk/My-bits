import os, asyncio, time, re, json, random
from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import SessionPasswordNeededError, FloodWaitError, UserNotParticipantError

# --- [ إعدادات القوة القصوى ] ---
API_ID = 25880715 
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'
DEVELOPER_ID = 7515408355 
CHANNEL_USER = 'WC_CR7' 

SESSION_DIR = 'user_sessions'
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

bot = TelegramClient('master_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- [ أزرار الكيبورد V12 ] ---
MAIN_KB = [
    ['🚀 الضربة القاضية (هجوم شامل)'],
    ['➕ إضافة جندي', '🗑️ تنظيف الحسابات'],
    ['🔍 فحص القوة', '📊 إحصائيات الجيش'],
    ['📢 قناة المطور']
]

# --- [ الدوال الذكية ] ---
async def internal_attack(session, target, reasons):
    client = TelegramClient(f"{SESSION_DIR}/{session}", API_ID, API_HASH)
    try:
        await client.connect()
        if await client.is_user_authorized():
            # إرسال بلاغات متعددة الأسباب من نفس الحساب
            for r in reasons:
                await client(functions.messages.ReportRequest(peer=target, id=[0], reason=r))
                await asyncio.sleep(0.3)
            return True
    except: return False
    finally: await client.disconnect()

# --- [ معالج الأوامر ] ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id != DEVELOPER_ID:
        try: await bot(functions.channels.GetParticipantRequest(CHANNEL_USER, event.sender_id))
        except: return await event.respond(f"⚠️ اشترك أولاً: @{CHANNEL_USER}", buttons=[Button.url("اضغط هنا", f"https://t.me/{CHANNEL_USER}")])
    await event.respond("🛡️ **أهلاً بك يا قائد في النسخة V12 - الضربة القاضية**", buttons=MAIN_KB)

@bot.on(events.NewMessage)
async def handle_kb(event):
    txt = event.text
    uid = event.sender_id

    if txt == '➕ إضافة جندي':
        async with bot.conversation(uid) as conv:
            await conv.send_message("📱 أرسل الرقم مع المفتاح:")
            phone = (await conv.get_response()).text.strip().replace(" ", "")
            client = TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH)
            await client.connect()
            try:
                res = await client.send_code_request(phone)
                await conv.send_message("📩 حول الكود هنا:")
                otp = re.search(r'\b\d{5}\b', (await conv.get_response()).text)
                if otp:
                    try: await client.sign_in(phone, otp.group(0), phone_code_hash=res.phone_code_hash)
                    except SessionPasswordNeededError:
                        await conv.send_message("🔐 الباسورد (2FA):")
                        await client.sign_in(password=(await conv.get_response()).text)
                    await conv.send_message("✅ تم الانضمام للجيش.")
                else: await conv.send_message("❌ كود غير صحيح.")
            except Exception as e: await conv.send_message(f"❌ فشل: {e}")
            finally: await client.disconnect()

    elif txt == '🚀 الضربة القاضية (هجوم شامل)':
        async with bot.conversation(uid) as conv:
            await conv.send_message("🔗 أرسل يوزر أو رابط الهدف المراد تدميره:")
            target = (await conv.get_response()).text.strip()
            
            # جلب معلومات الهدف قبل البدء
            try:
                full = await bot(functions.users.GetFullUserRequest(id=target) if not target.startswith(('+', '@')) else functions.contacts.ResolveUsernameRequest(username=target.replace('@','')))
                info = f"🎯 **معلومات الهدف:**\n👤 الاسم: {getattr(full, 'user', full).first_name}\n🆔 ID: `{getattr(full, 'user', full).id}`"
            except: info = "⚠️ لم يتم التعرف على تفاصيل الهدف، لكن سنبدأ الهجوم."
            
            reasons_kb = [[Button.inline("🔥 ضربة شاملة (كل الأسباب)", data="kill_all")],
                          [Button.inline("إسبام", data="kill_spam"), Button.inline("إباحي", data="kill_porn")]]
            await conv.send_message(f"{info}\n\n📂 اختر نوع الضربة:", buttons=reasons_kb)
            bot.target_temp = target

    elif txt == '🗑️ تنظيف الحسابات':
        msg = await event.respond("⏳ جاري فحص الحسابات وحذف الميتة...")
        sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session') and f != 'master_bot.session']
        deleted = 0
        for s in sessions:
            client = TelegramClient(f"{SESSION_DIR}/{s.replace('.session','')}", API_ID, API_HASH)
            try:
                await client.connect()
                if not await client.is_user_authorized():
                    os.remove(f"{SESSION_DIR}/{s}"); deleted += 1
            except: os.remove(f"{SESSION_DIR}/{s}"); deleted += 1
            finally: await client.disconnect()
        await msg.edit(f"✅ تم التنظيف! حذف {deleted} حساب ميت.")

    elif txt == '🔍 فحص القوة' or txt == '📊 إحصائيات الجيش':
        count = len([f for f in os.listdir(SESSION_DIR) if f.endswith('.session') and f != 'master_bot.session'])
        await event.respond(f"📈 **إحصائيات الجيش:**\n\n🚀 عدد الحسابات: {count}\n⚡️ جاهزية الهجوم: 100%\n🛡️ حالة النظام: آمن")

@bot.on(events.CallbackQuery(pattern=r"kill_(.*)"))
async def attack_call(event):
    cmd = event.data.decode().split('_')[1]
    all_reasons = [types.InputReportReasonSpam(), types.InputReportReasonPornography(), 
                   types.InputReportReasonViolence(), types.InputReportReasonOther()]
    
    reason_map = {"spam": [types.InputReportReasonSpam()], "porn": [types.InputReportReasonPornography()], "all": all_reasons}
    reasons = reason_map.get(cmd, [types.InputReportReasonOther()])
    
    target = getattr(bot, 'target_temp', None)
    if not target: return await event.respond("❌ أعد إرسال الرابط.")
    
    sessions = [f.replace('.session', '') for f in os.listdir(SESSION_DIR) if f.endswith('.session') and f != 'master_bot.session']
    await event.edit(f"🌪️ **بدأ الإعصار بـ {len(sessions)} حساب.. انتظر التدمير.**")
    
    tasks = [internal_attack(s, target, reasons) for s in sessions]
    results = await asyncio.gather(*tasks)
    await event.respond(f"🏁 **انتهت الضربة القاضية!**\n✅ بلاغات ناجحة: {results.count(True)}\n⚠️ فشلت: {results.count(False)}")

print("👑 النسخة V12 النهائية تعمل الآن بأقصى طاقة..")
bot.run_until_disconnected()
