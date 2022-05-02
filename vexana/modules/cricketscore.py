import urllib.request
from bs4 import BeautifulSoup
from telethon import events
from telethon.tl import functions, types
from telethon.tl.types import *
from vexana import telethn as tbot


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


@tbot.on(events.NewMessage(pattern="/cs$"))
async def _(event):
    if event.fwd_from:
        return
    if event.is_group and not (
            await is_register_admin(event.input_chat, event.message.sender_id)
    ):
        await event.reply("🚨 Need Admin Pewer.. You can't use this command.. But you can use in my pm")
        return

    score_page = "http://static.cricinfo.com/rss/livescores.xml"
    page = urllib.request.urlopen(score_page)
    soup = BeautifulSoup(page, "html.parser")
    result = soup.find_all("description")
    Sed = "".join(match.get_text() + "\n\n" for match in result)
    await event.reply(
        f"<b><u>Match information gathered successful</b></u>\n\n\n<code>{Sed}</code>",
        parse_mode="HTML",
    )

    __help__ = """
 ❍ /Cricket*:* to know the current status about upcoming message.
"""


__mod_name__ = "Cricket"
