import asyncio
import logging
import os
from telethon import Button, TelegramClient, events
from telethon import events
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from vexana import telethn
from vexana import telethn as Client

spam_chats = []


@telethn.on(events.NewMessage(pattern="^/all ?(.*)"))
@telethn.on(events.NewMessage(pattern="^@all ?(.*)"))
async def mentionall(event):
    chat_id = event.chat_id
    if event.is_private:
        return await event.respond("This command can be use in groups and channels!")

    is_admin = False
    try:
        partici_ = await Client(GetParticipantRequest(event.chat_id, event.sender_id))
    except UserNotParticipantError:
        is_admin = False
    else:
        if isinstance(
                partici_.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)
        ):
            is_admin = True

    if event.pattern_match.group(1) and event.is_reply:
        return await event.respond("Give me one argument!")
    elif event.pattern_match.group(1):
        mode = "text_on_cmd"
        msg = event.pattern_match.group(1)
    elif event.is_reply:
        mode = "text_on_reply"
        msg = await event.get_reply_message()
        if msg is None:
            return await event.respond(
                "I can't mention members for older messages! (messages which are sent before I'm added to group)"
            )
    else:
        return await event.respond(
            "Reply to a message or give me some text to mention others!"
        )

    Spam = spam_chats.append(chat_id)
    usrnum = 0
    usrtxt = ""
    async for usr in Client.iter_participants(chat_id):
        if chat_id not in spam_chats:
            break
        usrnum += 1
        usrtxt += f"[{usr.first_name}](tg://user?id={usr.id}) "
        if usrnum == 5:
            if mode == "text_on_cmd":
                txt = f"{usrtxt}\n\n{msg}"
                await Client.send_message(chat_id, txt)
            elif mode == "text_on_reply":
                await msg.reply(usrtxt)
            await asyncio.sleep(2)
            usrnum = 0
            usrtxt = ""
    try:
        spam_chats.remove(chat_id)
    except:
        pass


@telethn.on(events.NewMessage(pattern="^/cancel$"))
async def cancel_spam(event):
    if event.chat_id not in spam_chats:
        return await event.respond("There is no proccess on going...")
    try:
        spam_chats.remove(event.chat_id)
    except:
        pass
    return await event.respond("Stopped { Lots OF LOve From AXel }.")


__mod_name__ = "Mentions"
