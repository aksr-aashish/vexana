from vexana import pbot as  bot
from vexana import EVENT_LOGS,  DRAGONS, DEV_USERS as DEVS
from vexana.utils import *
from pyrogram import filters
import vexana.modules.sql.global_bans_sql as sql
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client
import time
from pyrogram.types import Message


@bot.on_message(filters.command("scan", prefixes=["/", ".", "?", "-"]))
async def ban(Client, m: Message):
    if m.from_user.id not in DEVS:
        await m.reply_text("Only The Vampire of Blue moon Can Use Me")

    if m.from_user.id in DEVS and not m.reply_to_message:
        user = m.command[1]
        reason = m.text.replace(m.text.split(" ")[0], "").replace(user, "")
        enforcer = m.from_user.id

        if len(user) != 10:
            await m.reply_text("Invalid id")
            return

        if not user.isdigit():
            await m.reply_text("User ID Must Be Integer")
            return

        else:
            user = int(user)
            if user not in DEVS:
                x = sql.gban_user(user, reason, enforcer)
                buttons = [
                    [
                        InlineKeyboardButton(
                            "Support", url="https://t.me/Sylviorus_support")
                    ],
                    [
                        InlineKeyboardButton(
                            "Report", url="https://t.me/SylviorusReport")
                    ],
                ]

                await bot.send_message(
                    EVENT_LOGS,
                    f"""
#BANNED
**USER**: [{user}](tg://user?id={user})
**REASON**: {reason}
**ENFORCER**: [{enforcer}](tg://user?id={enforcer})
**CHAT_ID** : {m.chat.id}
""",
                    reply_markup=InlineKeyboardMarkup(buttons))
                await m.reply(x)
            else:
                await m.reply("Vampires Cant Be Banned!")

    if m.from_user.id in DEVS and m.reply_to_message:
        user = m.reply_to_message.from_user.id
        reason = m.text.replace(m.text.split(" ")[0], "")
        enforcer = m.from_user.id

        if user not in DEVS:
            user = int(user)
            buttons = [[
                InlineKeyboardButton("Support",
                                     url="https://t.me/Sylviorus_support"),
            ],
                       [
                           InlineKeyboardButton(
                               "Report", url="https://t.me/SylviorusReport"),
                       ]]
            x = sql.gban_user(user, reason, enforcer)
            await bot.send_message(EVENT_LOGS,
                                   f"""
#BANNED

**USER**: [{user}](tg://user?id={user})
**REASON**: {reason}
**ENFORCER**: [{enforcer}](tg://user?id={enforcer})
**CHAT_ID** : {m.chat.id}
**Message Link : {m.link}
""",
                                   reply_markup=InlineKeyboardMarkup(buttons))
            await m.reply(x)

        else:
            await m.reply("The Vampire of Blue moon can't be banned!")
