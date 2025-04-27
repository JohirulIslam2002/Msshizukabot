# bot.py

from telethon import TelegramClient, events, Button
import asyncio
from datetime import datetime
import pytz

# ========== কনফিগারেশন ==========
API_ID = 22543888
API_HASH = 'b2c46c23f8d4d7defea5f97bd31be085'
BOT_TOKEN = '8066991836:AAEL5eLrrg80fSn3ERFax4PHbjnN77ByGJs'

SOURCE_CHANNEL_ID = -1002599155469
TARGET_CHANNEL_ID = -1002194172569
CHANNEL_LINK = 'https://t.me/MrCocoMusic'
OWNER_USERNAME = 'TopMasterBd'
OWNER_ID = 6513525964

# ========== মেম্বার কাউন্ট ==========
join_count = 0
leave_count = 0

# ========== ক্লায়েন্ট ==========
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ========== Start কমান্ড ==========
@client.on(events.NewMessage())
async def start(event):
    if event.is_private:
        if event.sender_id == OWNER_ID:
            pass
        else:
            buttons = [
                [Button.url("আমাদের চ্যানেলে জয়েন করুন", CHANNEL_LINK)],
                [Button.url("বট বানাতে যোগাযোগ করুন", f"https://t.me/{OWNER_USERNAME}")]
            ]
            welcome_text = f"""
স্বাগতম {event.sender.first_name}!

✅ আমাদের চ্যানেলে জয়েন করুন নতুন কনটেন্ট পেতে।
✅ যদি এমন বট বানাতে চান, যোগাযোগ করুন আমার সাথে।

ধন্যবাদ!
"""
            await event.respond(welcome_text, buttons=buttons)

# ========== নতুন মেম্বার ==========
@client.on(events.ChatAction(chats=TARGET_CHANNEL_ID))
async def member_update(event):
    global join_count, leave_count

    if event.user_joined or event.user_added:
        join_count += 1
        new_member = await event.get_user()
        username = new_member.username or new_member.first_name

        async for message in client.iter_messages(SOURCE_CHANNEL_ID, limit=100):
            if message.video:
                await client.send_file(
                    TARGET_CHANNEL_ID,
                    message.file,
                    caption=None
                )
                break

        mention_text = f"@{username} তোমাকে ধন্যবাদ জয়েন করার জন্য!\nবন্ধুদের আমন্ত্রণ জানাও নতুন ভিডিও পেতে!"
        buttons = [[Button.url("বন্ধুদের আমন্ত্রণ জানান", CHANNEL_LINK)]]

        sent_message = await client.send_message(
            TARGET_CHANNEL_ID,
            mention_text,
            buttons=buttons
        )

        await asyncio.sleep(30)
        await client.delete_messages(TARGET_CHANNEL_ID, [sent_message.id])

    elif event.user_left or event.user_kicked:
        leave_count += 1

# ========== রাত ১২টায় রিপোর্ট ==========
async def send_daily_report():
    global join_count, leave_count

    await client.connect()
    while True:
        now = datetime.now(pytz.timezone('Asia/Dhaka'))
        if now.hour == 0 and now.minute == 0:
            entity = await client.get_entity(TARGET_CHANNEL_ID)
            members = await client.get_participants(entity)
            total_members = len(members)

            report_text = f"""
✨ দৈনিক চ্যানেল রিপোর্ট:

➕ নতুন সদস্য: {join_count}
➖ হারানো সদস্য: {leave_count}
👥 মোট সদস্য সংখ্যা: {total_members}

-- রিপোর্ট বট
"""

            await client.send_message(OWNER_ID, report_text)

            join_count = 0
            leave_count = 0

        await asyncio.sleep(60)

# ========== রান ==========
async def main():
    await asyncio.gather(
        client.start(),
        send_daily_report()
    )

client.loop.run_until_complete(main())
