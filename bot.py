import asyncio
import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

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

spam_chats = {}

# 🔥 CHANGE THESE LINKS
OWNER = "https://t.me/your_username"
SUPPORT = "https://t.me/your_support_group"
UPDATES = "https://t.me/your_updates_channel"


# ===================== START COMMAND =====================

@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👑 Owner", url=OWNER),
                InlineKeyboardButton("💬 Support", url=SUPPORT)
            ],
            [
                InlineKeyboardButton("📢 Updates", url=UPDATES)
            ]
        ]
    )

    await message.reply(
        "👋 **Welcome to UTag Bot**\n\n"
        "⚡ Fast & Powerful Tagging Bot\n\n"
        "🔹 /utag hello → Tag all members\n"
        "🔹 Use buttons to control tagging\n\n"
        "🔥 Made with ❤️",
        reply_markup=buttons
    )


# ===================== UTAG COMMAND =====================

@app.on_message(filters.command("utag") & filters.group)
async def tag_all(client: Client, message: Message):

    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ):
        return await message.reply("🚫 Only Admins Can Use This Command.")

    if message.chat.id in spam_chats:
        return await message.reply("⚠️ Tagging already running.")

    custom_text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""

    spam_chats[message.chat.id] = True

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛑 Stop Tagging", callback_data=f"stop_{message.chat.id}")]
        ]
    )

    await message.reply(
        "🚀 Tagging Started...\nUse button to stop.",
        reply_markup=buttons
    )

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
        spam_chats.pop(message.chat.id, None)


# ===================== CALLBACK BUTTON =====================

@app.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):

    data = callback.data

    if data.startswith("stop_"):
        chat_id = int(data.split("_")[1])

        if chat_id in spam_chats:
            spam_chats.pop(chat_id, None)
            await callback.message.edit_text("🛑 Tagging Stopped Successfully.")
        else:
            await callback.answer("❌ Already stopped", show_alert=True)


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

    spam_chats.pop(message.chat.id, None)
    await message.reply("🚫 Tagging Cancelled Successfully.")


# ===================== RUN BOT =====================

print("Bot Started Successfully ✅")
app.run()
