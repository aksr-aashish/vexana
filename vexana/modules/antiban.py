from pyrogram import Client, filters
from pyrogram.raw import types, functions
from pyrogram.raw.base import Update


@Client.on_raw_update()
async def channel_handler(client: Client, update: Update, _, chats: dict):
    while True:
        try:
            # Check for message that are from channel
            if not isinstance(update, types.UpdateNewChannelMessage) or not isinstance(
                    update.message.from_id, types.PeerChannel
            ):
                return
            # Basic data
            message = update.message
            chat_id = int(f"-100{message.peer_id.channel_id}")
            channel_id = int(f"-100{message.from_id.channel_id}")
            # Check enable or not
            # Check for linked or free channel
            if (
                    (
                            message.fwd_from
                            and message.fwd_from.saved_from_peer
                            == message.fwd_from.from_id
                            == message.from_id
                    )
                    or channel_id == chat_id
            ):
                return
            # Delete the message sent by channel and ban it
            await client.send(
                functions.channels.EditBanned(
                    channel=await client.resolve_peer(chat_id),
                    participant=await client.resolve_peer(channel_id),
                    banned_rights=types.ChatBannedRights(
                        until_date=0,
                        view_messages=True,
                        send_messages=True,
                        send_media=True,
                        send_stickers=True,
                        send_gifs=True,
                        send_games=True,
                        send_polls=True,
                    ),
                )
            )
            await client.delete_messages(chat_id, message.id)
            await client.send_message(
                int(chat_id),
                f"#𝙰𝙽𝚃𝙸𝙲𝙷𝙰𝙽𝙽𝙴𝙻\n\n᛭ 𝚂𝙴𝙽𝙳𝙴𝚁 𝙸𝙳: `{channel_id}`\n᛭ 𝚃𝙰𝙺𝙴𝙽 𝙰𝙲𝚃𝙸𝙾𝙽: `DELETE BAN`",
                disable_web_page_preview=True,
            )
            break
        except Exception as e:
            print(e)
            break


from vexana import pbot
from vexana import EVENT_LOGS as LOGS
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery


@pbot.on_message()
def watch(_, m: Message):
    try:
        if "spam" in m.text or "Spam" in m.text and m.from_user.id:
            k = m.forward(-1001553435601)
            bot.send_message(
                -1001553435601, f"""
    ╒═══「<b>**✪Spammer_ADDED:</b> 」\n
    **Spamticker Detected an Spam**
    ✪Chat:-{html.escape(chat.title)}
    ✪Username : {m.chat.id}
    ✪Link Here :  {m.link}
    ✪Username Here : {m.chat.username}
    ✪Report an bug or issue at @axel_0p
    """)

    except FloodWait as e:
        asyncio.sleep(e.x)
    except Exception as e:
        print(e)
