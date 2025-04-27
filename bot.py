from telethon import TelegramClient, events, Button
import asyncio
from datetime import datetime, timedelta
import pytz

# ========== কনফিগারেশন ==========
API_ID = 22543888  # তোমার API_ID
API_HASH = 'b2c46c23f8d4d7defea5f97bd31be085'  # তোমার API_HASH
BOT_TOKEN = '8066991836:AAEL5eLrrg80fSn3ERFax4PHbjnN77ByGJs'  # তোমার Bot Token

SOURCE_CHANNEL_ID = -1002599155469  # সোর্স চ্যানেল আইডি
TARGET_CHANNEL_ID = -1002194172569  # টার্গেট চ্যানেল আইডি
CHANNEL_LINK = 'https://t.me/MrCocoMusic'  # তোমার চ্যানেলের লিঙ্ক
OWNER_USERNAME = 'TopMasterBd'  # তোমার টেলিগ্রাম ইউজারনেম
OWNER_ID = 6513525964  # তোমার চ্যাট আইডি (তুমি যেখানে রিপোর্ট পাবে)

# ========== মেম্বার কাউন্ট সেটাপ ==========
join_count = 0
leave_count = 0

# ========== ক্লায়েন্ট সেটাপ ==========
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ========== Start কমান্ড ও প্রাইভেট চ্যাট ==========
@client.on(events.NewMessage())
async def start(event):
    if event.is_private:
        if event.sender_id == OWNER_ID:
            # Owner হলে সব মেসেজ চলবে
            pass
        else:
            # অন্য কেউ মেসেজ দিলে শুধু ওয়েলকাম মেসেজ যাবে
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

# ========== নতুন মেম্বার জয়েন হলে ==========
@client.on(events.ChatAction(chats=TARGET_CHANNEL_ID))
async def member_update(event):
    global join_count, leave_count

    if event.user_joined or event.user_added:
        join_count += 1
        new_member = await event.get_user()
        username = new_member.username or new_member.first_name

        # সোর্স থেকে ভিডিও বের করা
        async for message in client.iter_messages(SOURCE_CHANNEL_ID, limit=100):
            if message.video:
                await client.send_file(
                    TARGET_CHANNEL_ID,
                    message.file,
                    caption=None
                )
                break

        # মেনশনসহ টেক্সট
        mention_text = f"@{username} তোমাকে ধন্যবাদ জয়েন করার জন্য!\nবন্ধুদের আমন্ত্রণ জানাও নতুন ভিডিও পেতে!"

        buttons = [
            [Button.url("বন্ধুদের আমন্ত্রণ জানান", CHANNEL_LINK)]
        ]

        sent_message = await client.send_message(
            TARGET_CHANNEL_ID,
            mention_text,
            buttons=buttons
        )

        await asyncio.sleep(30)
        await client.delete_messages(TARGET_CHANNEL_ID, [sent_message.id])

    elif event.user_left or event.user_kicked:
        leave_count += 1

# ========== চ্যানেল Join Request Auto Approve ==========
@client.on(events.ChatActionRequest())
async def auto_approve(event):
    await event.approve()

# ========== রাত ১২টায় Owner কে রিপোর্ট পাঠানো ==========
async def send_daily_report():
    await client.connect()
    while True:
        now = datetime.now(pytz.timezone('Asia/Dhaka'))
        if now.hour == 0 and now.minute == 0:  # রাত ১২:০০
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

            # কাউন্ট রিসেট
            global join_count, leave_count
            join_count = 0
            leave_count = 0

        await asyncio.sleep(60)  # প্রতি মিনিটে চেক করবে

# ========== রান ==========
async def main():
    await asyncio.gather(
        client.start(),
        send_daily_report()
    )

client.loop.run_until_complete(main())
