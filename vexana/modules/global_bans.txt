import html
import time
from datetime import datetime
from io import BytesIO

from telegram import ParseMode, Update
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.error import BadRequest, TelegramError, Unauthorized
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

import vexana.modules.sql.global_bans_sql as sql
from vexana.modules.sql.users_sql import get_user_com_chats
from vexana import (
    DEV_USERS,
    EVENT_LOGS,
    OWNER_ID,
    STRICT_GBAN,
    DRAGONS,
    SUPPORT_CHAT,
    SPAMWATCH_SUPPORT_CHAT,
    DEMONS,
    TIGERS,
    WOLVES,
    sw,
    dispatcher,
)
from vexana.modules.helper_funcs.chat_status import (
    is_user_admin,
    support_plus,
    user_admin,
)
from vexana.modules.helper_funcs.extraction import (
    extract_user,
    extract_user_and_text,
)
from vexana.modules.helper_funcs.misc import send_to_list

GBAN_ENFORCE_GROUP = 6

GBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to kick it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can kick group administrators",
    "Channel_private",
    "Not in the chat",
    "Can't remove chat owner",
}

UNGBAN_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Method is available for supergroup and channel chats only",
    "Not in the chat",
    "Channel_private",
    "Chat_admin_required",
    "Peer_id_invalid",
    "User not found",
}

buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="𝗨𝗽𝗱𝗮𝘁𝗲𝘀", url="https://t.me/Updates",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="𝗥𝗲𝗾𝘂𝗲𝘀𝘁", url="https://t.me/vexana_Support",
                    ),
                ],
            ],
        ),

@support_plus
def gban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return

    if int(user_id) in DEV_USERS:
        message.reply_text(
            "That user is an part of VexanaFAnclub \n I can't act against our own.",
        )
        return

    if int(user_id) in DRAGONS:
        message.reply_text(
            "I spy, with my little eye... a disaster! Why are you guys turning on each other?",
        )
        return

    if int(user_id) in DEMONS:
        message.reply_text(
            "OOOH someone's trying to Blacklisted a Demon Disaster! ",
        )
        return

    if int(user_id) in TIGERS:
        message.reply_text("That's a Tiger! They cannot be Blacklisted!")
        return

    if int(user_id) in WOLVES:
        message.reply_text("That's a Wolf! They cannot be Blacklisted!")
        return

    if user_id == bot.id:
        message.reply_text("You uhh...want me to punch myself?")
        return

    if user_id in [777000, 1087968824]:
        message.reply_text("Fool! You can't attack Telegram's native tech!")
        return

    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return ""
        return

    if user_chat.type != "private":
        message.reply_text("That's not a user!")
        return

    if sql.is_user_gbanned(user_id):

        if not reason:
            message.reply_text(
                "This user is already Blacklisted; I'd change the reason, but you haven't given me one...",
            )
            return

        old_reason = sql.update_gban_reason(
            user_id,
            user_chat.username or user_chat.first_name,
            reason,
        )
        if old_reason:
            message.reply_text(
                "This user is already Blacklisted, for the following reason:\n"
                "<code>{}</code>\n"
                "I've gone and updated it with your new reason!".format(
                    html.escape(old_reason),
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            message.reply_text(
                "This user is already Blacklisted, but had no reason set; I've gone and updated it!",
            )

        return

    message.reply_text("𝙎𝙘𝙖𝙣𝙞𝙣𝙜 𝙐𝙨𝙚𝙧 𝙞𝙣 𝙈𝙮 𝘿𝙖𝙩𝙖𝘽𝙖𝙨𝙚")

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = "<b>{} ({})</b>\n".format(html.escape(chat.title), chat.id)
    else:
        chat_origin = "<b>{}</b>\n".format(chat.id)
        
    log_message =(
        f"<b>𝐁𝐥𝐚𝐜𝐤𝐥𝐢𝐬𝐭𝐢𝐧𝐠 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝</b>\n"
        f"<b>𝙏𝙧𝙖𝙘𝙚𝙙 𝙁𝙧𝙤𝙢:</b> <code>{chat_origin}</code>\n"
        f"<b>𝐄𝐧𝐟𝐨𝐫𝐜𝐞𝐫:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>𝐁𝐚𝐧𝐧𝐞𝐝 𝐔𝐬𝐞𝐫:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>𝗕𝗮𝗻𝗻𝗲𝗱 𝗨𝘀𝗲𝗿 ID:</b> <code>{user_chat.id}</code>\n"
        f"<b>𝐒𝐢𝐠𝐧:</b> <code>{current_time}</code>",
    ),
    
    if reason:
        if chat.type == chat.SUPERGROUP and chat.username:
            log_message += f'\n<b>Reason:</b> <a href="https://telegram.me/{chat.username}/{message.message_id}">{reason}</a> '
        else:
            log_message += f"\n<b>Reason:</b> <code>{reason}</code>,"

    if EVENT_LOGS:
        try:
            log = bot.send_message(EVENT_LOGS, log_message, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            log = bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\nFormatting has been disabled due to an unexpected error.",
            )

    else:
        send_to_list(bot, DRAGONS + DEMONS, log_message, html=True)

    sql.gban_user(user_id, user_chat.username or user_chat.first_name, reason)

    chats = get_user_com_chats(user_id)
    gbanned_chats = 0

    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            bot.ban_chat_member(chat_id, user_id)
            gbanned_chats += 1

        except BadRequest as excp:
            if excp.message not in GBAN_ERRORS:
                message.reply_text(f"Could not blacklist due to: {excp.message}")
                if EVENT_LOGS:
                    bot.send_message(
                        EVENT_LOGS,   
                        f"Could not blacklist due to {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    send_to_list(
                        bot,
                        DRAGONS + DEMONS,
                        f"Could not blacklist due to: {excp.message}",
                    )
                sql.ungban_user(user_id)
                return
        except TelegramError:
            pass

    if EVENT_LOGS:
        log.edit_text(
            log_message + f"\n<b>Total affected Chat:</b> <code>{gbanned_chats}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(
            bot,
            DRAGONS + DEMONS,
            f"𝗘𝗻𝗳𝗼𝗿𝗰𝗲𝗱 𝗮 𝗿𝗲𝗺𝗼𝘁𝗲 𝘀𝗰𝗮𝗻! (𝗨𝘀𝗲𝗿 𝗯𝗮𝗻𝗻𝗲𝗱 𝗶𝗻 <code>{gbanned_chats}</code> chats)",
            html=True,
        )

    end_time = time.time()
    gban_time = round((end_time - start_time), 2)

    if gban_time > 60:
        gban_time = round((gban_time / 60), 2)
    message.reply_text("𝗘𝗻𝗳𝗼𝗿𝗰𝗲𝗱 𝗮 𝗿𝗲𝗺𝗼𝘁𝗲 𝘀𝗰𝗮𝗻.", parse_mode=ParseMode.HTML)
    try:
        bot.send_message(
            user_id,
            "#EVENT"
            "You have been marked as Malicious and as such have been banned from any future groups we manage."
            f"\n<b>Reason:</b> <code>{html.escape(user.reason)}</code>"
            f"</b>Appeal Chat:</b> @{SUPPORT_CHAT}",
            parse_mode=ParseMode.HTML,
        )
    except:
        pass  # bot probably blocked by user


@support_plus
def ungban(update: Update, context: CallbackContext):  # sourcery no-metrics
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "Inncorrect User Id Or UserName..",
        )
        return

    user_chat = bot.get_chat(user_id)
    if user_chat.type != "private":
        message.reply_text("That's not a user!")
        return

    if not sql.is_user_gbanned(user_id):
        message.reply_text("This user is not gbanned!")
        return

    message.reply_text(f"Unblacklisting {user_chat.first_name} Giving an another chance.")

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = f"<b>{html.escape(chat.title)} ({chat.id})</b>\n"
    else:
        chat_origin = f"<b>{chat.id}</b>\n"

    log_message = (
        f"𝗨𝗻𝗯𝗹𝗮𝗰𝗸𝗹𝗶𝘀𝘁𝗶𝗻𝗴 𝗖𝗼𝗺𝗽𝗹𝘁𝗲𝗱 #𝗹𝗼𝗴𝘀\n"
        f"<b>𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗲𝗱 𝗙𝗿𝗼𝗺:</b> <code>{chat_origin}</code>\n"
        f"<b>Enforcer:</b>  [Vexana AI](https://gban-api.up.railway.app/user/:userid)\n"
        f"<b>Unbanned User:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>Unbanned User ID:</b> <code>{user_chat.id}</code>\n"
        f"<b>Stamp:</b> <code>{current_time}</code>",
        
        ),

    if EVENT_LOGS:
        try:
            log = bot.send_message(EVENT_LOGS, log_message, parse_mode=ParseMode.HTML,disable_web_page_preview=True,)
        except BadRequest as excp:
            log = bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\nFormatting has been disabled due to an unexpected error.",
            )
    else:
        send_to_list(bot, DRAGONS + DEMONS, log_message, html=True)

    chats = get_user_com_chats(user_id)
    ungbanned_chats = 0

    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == "kicked":
                bot.unban_chat_member(chat_id, user_id)
                ungbanned_chats += 1

        except BadRequest as excp:
            if excp.message not in UNGBAN_ERRORS:
                message.reply_text(f"Could not Unblacklisting due to: {excp.message}")
                if EVENT_LOGS:
                    bot.send_message(
                        EVENT_LOGS,
                        f"Could not Unblacklisting due to: {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    bot.send_message(
                        OWNER_ID,
                        f"Could not Unblacklisting due to: {excp.message}",
                    )
                return
        except TelegramError:
            pass

    sql.ungban_user(user_id)

    if EVENT_LOGS:
        log.edit_text(
            log_message + f"\n<b>Total affected chat :</b> {ungbanned_chats}",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(bot, DRAGONS + DEMONS, "Unblacklisting in progress!")

    end_time = time.time()
    ungban_time = round((end_time - start_time), 2)

    if ungban_time > 60:
        ungban_time = round((ungban_time / 60), 2)
        message.reply_text(f"Unblacklisting successful. Total Time taken {ungban_time} min")
    else:
        message.reply_text(f"Unblacklisting successful. Total Time taken {ungban_time} sec")


@support_plus
def gbanlist(update: Update, context: CallbackContext):
    banned_users = sql.get_gban_list()

    if not banned_users:
        update.effective_message.reply_text(
            "There aren't any gbanned users!",
        )
        return

    banfile = "Screw these guys.\n"
    for user in banned_users:
        banfile += f"[x] {user['name']} - {user['user_id']}\n"
        if user["reason"]:
            banfile += f"Reason: {user['reason']}\n"

    with BytesIO(str.encode(banfile)) as output:
        output.name = "gbanlist.txt"
        update.effective_message.reply_document(
            document=output,
            filename="gbanlist.txt",
            caption="Here is the list of currently gbanned users.",
        )


def check_and_ban(update, user_id, should_message=True):

    if user_id in TIGERS or user_id in WOLVES:
        sw_ban = None
    else:
        try:
            sw_ban = sw.get_ban(int(user_id))
        except:
            sw_ban = None

    if sw_ban:
        update.effective_chat.ban_member(user_id)
        if should_message:
            update.effective_message.reply_text(
                f"<b>Alert</b>: this user is globally banned.\n"
                f"<code>*bans them from here*</code>.\n"
                f"<b>Appeal chat</b>: {SPAMWATCH_SUPPORT_CHAT}\n"
                f"<b>User ID</b>: <code>{sw_ban.id}</code>\n"
                f"<b>Ban Reason</b>: <code>{html.escape(sw_ban.reason)}</code>",
                parse_mode=ParseMode.HTML,
            )
        return

    if sql.is_user_gbanned(user_id):
        update.effective_chat.ban_member(user_id)
        if should_message:
            text = (
                f"<b>This User is mark as Threat by my Owners or any Sudo User.\n"
                f"<b>Support chat</b>: @{SUPPORT_CHAT}\n"
                f"<b>User ID</b>: <code>{user_id}</code>"
            )
            user = sql.get_gbanned_user(user_id)
            if user.reason:
                text += f"\n<b>Following Reason :</b> <code>{html.escape(user.reason)}</code>"
            update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


def enforce_gban(update: Update, context: CallbackContext):
    # Not using @restrict handler to avoid spamming - just ignore if cant gban.
    bot = context.bot
    try:
        restrict_permission = update.effective_chat.get_member(
            bot.id,
        ).can_restrict_members
    except Unauthorized:
        return
    if sql.does_chat_gban(update.effective_chat.id) and restrict_permission:
        user = update.effective_user
        chat = update.effective_chat
        msg = update.effective_message

        if user and not is_user_admin(chat, user.id):
            check_and_ban(update, user.id)
            return

        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                check_and_ban(update, mem.id)

        if msg.reply_to_message:
            user = msg.reply_to_message.from_user
            if user and not is_user_admin(chat, user.id):
                check_and_ban(update, user.id, should_message=False)


@user_admin
def gbanstat(update: Update, context: CallbackContext):
    args = context.args
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_gbans(update.effective_chat.id)
            update.effective_message.reply_text(
                "Antispam is now enabled ✅ "
                "I am now protecting your group from potential remote threats!",
            )
        elif args[0].lower() in ["off", "no"]:
            sql.disable_gbans(update.effective_chat.id)
            update.effective_message.reply_text(
                "Antispan is now disabled ❌ " "Spamwatch is now disabled ❌",
            )
    else:
        update.effective_message.reply_text(
            "Give me some arguments to choose a setting! on/off, yes/no!\n\n"
            "Your current setting is: {}\n"
            "When True, any gbans that happen will also happen in your group. "
            "When False, they won't, leaving you at the possible mercy of "
            "spammers.".format(sql.does_chat_gban(update.effective_chat.id)),
        )


def __stats__():
    return f"× {sql.num_gbanned_users()} gbanned users."


def __user_info__(user_id):
    is_gbanned = sql.is_user_gbanned(user_id)
    text = "Malicious: <b>{}</b>"
    if user_id in [777000, 1087968824]:
        return ""
    if user_id == dispatcher.bot.id:
        return ""
    if int(user_id) in DRAGONS + TIGERS + WOLVES:
        return ""
    if is_gbanned:
        text = text.format("Yes")
        user = sql.get_gbanned_user(user_id)
        if user.reason:
            text += f"\n<b>Reason:</b> <code>{html.escape(user.reason)}</code>"
        text += f"\n<b>Appeal Chat:</b> @{SUPPORT_CHAT}"
    else:
        text = text.format("???")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"This chat is enforcing *gbans*: `{sql.does_chat_gban(chat_id)}`."


__help__ = f"""
*Admins only:*
❂ `/antispam <on/off/yes/no>`*:* Will toggle our antispam tech or return your current settings.

Anti-Spam, used by bot devs to ban spammers across all groups. This helps protect \
you and your groups by removing spam flooders as quickly as possible.
*Note:* Users can appeal gbans or report spammers at @{SUPPORT_CHAT}

This also integrates @Spamwatch API to remove Spammers as much as possible from your chatroom!
*What is SpamWatch?*
SpamWatch maintains a large constantly updated ban-list of spambots, trolls, bitcoin spammers and unsavoury characters[.](https://telegra.ph/file/f584b643c6f4be0b1de53.jpg)
Constantly help banning spammers off from your group automatically So, you wont have to worry about spammers storming your group.
*Note:* Users can appeal spamwatch bans at @SpamwatchSupport
"""

GBAN_HANDLER = CommandHandler("gban", gban, run_async=True)
UNGBAN_HANDLER = CommandHandler("ungban", ungban, run_async=True)
GBAN_LIST = CommandHandler("gbanlist", gbanlist, run_async=True)
GBAN_STATUS = CommandHandler(
    "antispam", gbanstat, filters=Filters.chat_type.groups, run_async=True
)
GBAN_ENFORCER = MessageHandler(
    Filters.all & Filters.chat_type.groups, enforce_gban, run_async=True
)

dispatcher.add_handler(GBAN_HANDLER)
dispatcher.add_handler(UNGBAN_HANDLER)
dispatcher.add_handler(GBAN_LIST)
dispatcher.add_handler(GBAN_STATUS)

__mod_name__ = "Anti-Spam"
__handlers__ = [GBAN_HANDLER, UNGBAN_HANDLER, GBAN_LIST, GBAN_STATUS]

if STRICT_GBAN:  # enforce GBANS if this is set
    dispatcher.add_handler(GBAN_ENFORCER, GBAN_ENFORCE_GROUP)
    __handlers__.append((GBAN_ENFORCER, GBAN_ENFORCE_GROUP))
