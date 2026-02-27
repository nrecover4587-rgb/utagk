import asyncio
import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message

# 🔐 Heroku Config Vars
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client(
    "UtagBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

spam_chats = set()


# ===================== START COMMAND =====================

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply(
        "👋 Hello!\n\n"
        "I'm UTag Bot.\n\n"
        "🔹 /utag hello → Tag all members with message\n"
        "🔹 /cancel → Stop tagging (Admin Only)"
    )


# ===================== UTAG COMMAND =====================

@app.on_message(filters.command("utag") & filters.group)
async def tag_all(client: Client, message: Message):

    # 🔒 Admin Check
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ):
        return await message.reply("🚫 Only Admins Can Use This Command.")

    if message.chat.id in spam_chats:
        return await message.reply("⚠️ Tagging already running.")

    custom_text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""

    spam_chats.add(message.chat.id)
    total = 0
    count = 0
    users_text = ""

    try:
        async for member in client.get_chat_members(message.chat.id):

            if message.chat.id not in spam_chats:
                break

            if not member.user or member.user.is_bot:
                continue

            user = member.user
            name = user.first_name.replace("[", "").replace("]", "")
            mention = f"[{name}](tg://user?id={user.id})"

            users_text += f"➤ {mention}\n"
            total += 1
            count += 1

            if count == 5:
                try:
                    msg = f"{custom_text}\n\n{users_text}" if custom_text else users_text
                    await message.reply_text(msg)
                except FloodWait as e:
                    await asyncio.sleep(e.value)

                await asyncio.sleep(2)
                users_text = ""
                count = 0

        if users_text:
            msg = f"{custom_text}\n\n{users_text}" if custom_text else users_text
            await message.reply_text(msg)

        await message.reply(f"✅ Tagging Completed\n👥 Total Users: {total}")

    finally:
        spam_chats.discard(message.chat.id)


# ===================== CANCEL COMMAND =====================

@app.on_message(filters.command("cancel") & filters.group)
async def cancel_tagging(client: Client, message: Message):

    if message.chat.id not in spam_chats:
        return await message.reply("❌ No tagging running.")

    member = await client.get_chat_member(message.chat.id, message.from_user.id)

    if member.status not in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ):
        return await message.reply("🚫 Only Admins Can Cancel.")

    spam_chats.discard(message.chat.id)
    await message.reply("🚫 Tagging Cancelled Successfully.")


# ===================== RUN BOT =====================

print("Bot Started Successfully ✅")
app.run()
