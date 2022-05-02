import asyncio
import motor.motor_asyncio
import os
from pyrogram import filters
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from vexana import MONGO_DB_URI
from vexana import pbot
from vexana import pgram
from vexana.utils.dbfunc import (antiservice_off, antiservice_on,
                                 is_antiservice_on)
# from wbb import app
from vexana.utils.permissions import adminsOnly


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    async def add_chat_list(self, chat_id, ch_id=None):
        get_chat = await self.is_chat_exist(chat_id)
        if get_chat:
            chat_list = list(get_chat.get("chats"))
            if ch_id != None and int(ch_id) in chat_list:
                return True, f"{ch_id} already in white list."
            elif ch_id == None:
                return False, ""
            elif ch_id is not None:
                chat_list.append(int(ch_id))
                await self.col.update_one(
                    {"id": chat_id}, {"$set": {"chats": chat_list}}
                )
                return True, f"{ch_id}, added into white list"
        a_chat = {"id": int(chat_id), "chats": [ch_id]}
        await self.col.insert_one(a_chat)
        return False, ""

    async def is_chat_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user if user else False

    async def get_chat_list(self, chat_id):
        get_chat = await self.is_chat_exist(chat_id)
        if get_chat:
            return get_chat.get("chats", [])
        else:
            return False

    async def del_chat_list(self, chat_id, ch_id=None):
        get_chat = await self.is_chat_exist(chat_id)
        if get_chat:
            chat_list = list(get_chat.get("chats"))
            if ch_id != None and ch_id in chat_list:
                chat_list.remove(int(ch_id))
                await self.col.update_one(
                    {"id": chat_id}, {"$set": {"chats": chat_list}}
                )
                return True, f"{ch_id}, removed from white list"
            elif int(ch_id) not in chat_list:
                return True, f"{ch_id}, not found in white list."

    async def delete_chat_list(self, chat_id):
        await self.col.delete_many({"id": int(chat_id)})


db = Database(MONGO_DB_URI, "VEXANA")


@pbot.on_message(filters.command("antiservice") & ~filters.private)
@adminsOnly("can_change_info")
async def anti_service(_, message):
    if len(message.command) != 2:
        return await message.reply_text(
            "Usage: /antiservice [enable | disable]"
        )
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "enable":
        await antiservice_on(chat_id)
        await message.reply_text(
            "Enabled AntiService System. I will Delete Service Messages from Now on."
        )
    elif status == "disable":
        await antiservice_off(chat_id)
        await message.reply_text(
            "Disabled AntiService System. I won't Be Deleting Service Message from Now on."
        )
    else:
        await message.reply_text(
            "Unknown Suffix, Use /antiservice [enable|disable]"
        )


@pbot.on_message(filters.service, group=11)
async def delete_service(_, message):
    chat_id = message.chat.id
    try:
        if await is_antiservice_on(chat_id):
            return await message.delete()
    except Exception:
        pass
