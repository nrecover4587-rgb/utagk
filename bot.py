import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message

# 🔹 Yaha apni details daalo
API_ID = 24168862
API_HASH = "916a9424dd1e58ab7955001ccc0172b3"
BOT_TOKEN = "8740569127:AAF8N60Y5Fn-o0M0oHUBOGQMSpAol1uIfRQ"

app = Client(
    "UtagBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

spam_chats = set()


@app.on_message(filters.command("utag") & filters.group)
async def tag_all(client: Client, message: Message):

    if message.chat.id in spam_chats:
        return await message.reply("⚠️ Already running tagging.")

    spam_chats.add(message.chat.id)
    total = 0
    count = 0
    text = ""

    try:
        async for member in client.get_chat_members(message.chat.id):

            if message.chat.id not in spam_chats:
                break

            if not member.user or member.user.is_bot:
                continue

            user = member.user
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            text += f"➤ {mention}\n"

            total += 1
            count += 1

            if count == 5:
                try:
                    await message.reply_text(f"{text}\n📢 Tagged: {total}")
                except FloodWait as e:
                    await asyncio.sleep(e.value)

                await asyncio.sleep(2)
                text = ""
                count = 0

        if text:
            await message.reply_text(f"{text}\n📢 Tagged: {total}")

        await message.reply(f"✅ Done! Total Users: {total}")

    finally:
        spam_chats.discard(message.chat.id)


@app.on_message(filters.command("cancel") & filters.group)
async def cancel(client: Client, message: Message):

    if message.chat.id not in spam_chats:
        return await message.reply("❌ Not running.")

    member = await client.get_chat_member(message.chat.id, message.from_user.id)

    if member.status not in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ):
        return await message.reply("Only admins can cancel.")

    spam_chats.discard(message.chat.id)
    await message.reply("🚫 Tagging Cancelled.")


print("Bot Started...")
app.run()
