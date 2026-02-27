import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, FloodWait
from pyrogram.types import Message

from ANNIEMUSIC import app
from ANNIEMUSIC.utils.admin_filters import admin_filter

spam_chats = set()


@app.on_message(filters.command(["utag", "all", "mention"]) & filters.group & admin_filter)
async def tag_all_users(client: Client, message: Message):
    if message.chat.id in spam_chats:
        return await message.reply("**⚠️ Already tagging in this chat.**")

    replied = message.reply_to_message
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else ""

    if not replied and not text:
        return await message.reply(
            "**Reply to a message or give some text to tag all.**"
        )

    spam_chats.add(message.chat.id)
    total_tagged = 0
    batch_count = 0
    user_text = ""

    try:
        async for member in client.get_chat_members(message.chat.id):

            if message.chat.id not in spam_chats:
                break

            if not member.user or member.user.is_bot:
                continue

            user = member.user
            name = user.first_name.replace("[", "").replace("]", "")
            mention = f"[{name}](tg://user?id={user.id})"

            user_text += f"➤ {mention}\n"
            batch_count += 1
            total_tagged += 1

            if batch_count == 5:
                try:
                    msg_text = f"{text}\n\n{user_text}\n📢 Tagged: {total_tagged}"
                    if replied:
                        await replied.reply_text(msg_text)
                    else:
                        await message.reply_text(msg_text)

                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    pass

                await asyncio.sleep(2)
                batch_count = 0
                user_text = ""

        # Remaining users
        if user_text:
            msg_text = f"{text}\n\n{user_text}\n📢 Tagged: {total_tagged}"
            if replied:
                await replied.reply_text(msg_text)
            else:
                await message.reply_text(msg_text)

        await message.reply(
            f"✅ **Tagging Completed Successfully**\n👥 Total Users: `{total_tagged}`"
        )

    finally:
        spam_chats.discard(message.chat.id)


@app.on_message(filters.command(["cancel", "ustop"]) & filters.group)
async def cancel_tagging(client: Client, message: Message):
    chat_id = message.chat.id

    if chat_id not in spam_chats:
        return await message.reply("**❌ I'm not tagging anyone right now.**")

    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)

        if member.status not in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        ):
            return await message.reply("**Only admins can cancel tagging.**")

    except UserNotParticipant:
        return await message.reply("**You are not a participant of this chat.**")
    except Exception:
        return await message.reply("**Error checking admin status.**")

    spam_chats.discard(chat_id)
    return await message.reply("**🚫 Tagging cancelled successfully.**")
