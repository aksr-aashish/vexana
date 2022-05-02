import html
import re
import time
import vexana.modules.sql.global_bans_sql as sql
from datetime import datetime
from io import BytesIO
from telegram import (Bot, Chat, InlineKeyboardButton, InlineKeyboardMarkup,
                      Message, ParseMode, Update, User)
from telegram.error import BadRequest, TelegramError
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler)
from telegram.utils.helpers import mention_html
from typing import List, Optional
from vexana import DEMONS as SUPPORT_USERS
from vexana import (DEV_USERS, GBAN_LOGS, OWNER_ID, STRICT_GBAN, dispatcher)
from vexana import DRAGONS as SUDO_USERS
from vexana import WOLVES as WHITELIST_USERS
from vexana.modules.helper_funcs.chat_status import is_user_admin, user_admin
from vexana.modules.helper_funcs.extraction import (extract_user,
                                                    extract_user_and_text)
from vexana.modules.helper_funcs.filters import CustomFilters
from vexana.modules.helper_funcs.misc import send_to_list
from vexana.modules.sql.users_sql import get_all_chats

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
    "Can't remove chat owner"
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
    "User not found"
}


def gban(update, context):
    args = context.args
    bot = context.bot
    message = update.effective_message  # type: Optional[Message] 
    chat = update.effective_chat

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return

    if int(user_id) == OWNER_ID:
        message.reply_text("User Status Owner Cant take any action")
        return

    if int(user_id) in DEV_USERS:
        message.reply_text("With His Little Hand Someone Trying To Ban a Apologypse.")
        return

    if int(user_id) in SUDO_USERS:
        message.reply_text("Yay There is Nothing I Can Do Because This User is Scorpion And I Scare With Scorpions😫")
        return

    if int(user_id) in SUPPORT_USERS:
        message.reply_text("Wew You Are Trying To Ban A Mortal So Sed:/")
        return

    if int(user_id) in WHITELIST_USERS:
        message.reply_text("I Can't Ban a Knight.")
        return

    if user_id == bot.id:
        message.reply_text("-_- So funny, lets gban myself why don't I? Nice try.")
        return

    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        message.reply_text(excp.message)
        return

    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return

    if sql.is_user_gbanned(user_id):

        if not reason:
            message.reply_text(
                "This user is already gbanned; I'd change the reason, but you haven't given me one...",
            )
            return

        old_reason = sql.update_gban_reason(
            user_id,
            user_chat.username or user_chat.first_name,
            reason,
        )
        if old_reason:
            message.reply_text(
                "This user is already gbanned, for the following reason:\n"
                "<code>{}</code>\n"
                "I've gone and updated it with your new reason!".format(
                    html.escape(old_reason),
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            message.reply_text(
                "This user is already gbanned, but had no reason set; I've gone and updated it!",
            )

        return

    message.reply_text(
        "Request Sent Successfully Waiting For Approval {link}(https://gban-api-production.up.railway.app/{user_id})")
    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = "<b>{} ({})</b>\n".format(html.escape(chat.title), chat.id)
    else:
        chat_origin = "<b>{}</b>\n".format(chat.id)

    banner = update.effective_user  # type: Optional[User]
    log_message = (
        "<b>ɴᴇᴡ ɢʙᴀɴ ʀᴇǫᴜᴇsᴛ</b>" \
        "\n#ᴡᴀɪᴛɪɴɢ_ғᴏʀ_ᴀᴘᴘʀᴏᴠᴀʟ" \
        "\n<b>Originated from:</b> {}" \
        "\n<b>Status:</b> <code>Enforcing</code>" \
        "\n<b>Targeted User:</b> {}" \
        "\n<b>User:</b> {}" \
        "\n<b>ID:</b> <code>{}</code>" \
        "\n<b>Event Stamp:</b> {}" \
        "\n<b>Reason:</b> {}".format(chat_origin, mention_html(banner.id, banner.first_name),
                                     mention_html(user_chat.id, user_chat.first_name),
                                     user_chat.id, current_time, reason or "No reason given"))

    if GBAN_LOGS:
        try:
            log = bot.send_message(
                GBAN_LOGS, log_message, parse_mode=ParseMode.HTML)
        except BadRequest as e:
            print(e)
            log = bot.send_message(
                GBAN_LOGS,
                log_message +
                "\n\nFormatting has been disabled due to an unexpected error.")

    try:
        owner_id = OWNER_ID
        if not reason:
            noreason = "No Reason Given"
            bot.send_message(
                GBAN_LOGS,
                "<b>New GBAN Request\nUser</b>: {}\nReason: <code>{}</code> \nRequest By Enforcer: {}".format(
                    mention_html(user_id, user_chat.first_name), noreason, mention_html(banner.id, banner.first_name)),
                parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Accept✅",
                                                                                                    callback_data="gbanbtn".format(
                                                                                                        user_id,
                                                                                                        noreason)),
                                                                               InlineKeyboardButton(text="Decline❌",
                                                                                                    callback_data="gbancancel")]]))

        else:
            bot.send_message(
                GBAN_LOGS, "New GBAN Request\nUser: {}\nReason: <code>{}</code> \nRequest By Enforcer: {}".format(
                    mention_html(user_id, user_chat.first_name), reason, mention_html(banner.id, banner.first_name)),
                parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Accept✅",
                                                                                                    callback_data="gbanbtn_({})({})".format(
                                                                                                        user_id,
                                                                                                        reason)),
                                                                               InlineKeyboardButton(text="Decline❌",
                                                                                                    callback_data="gbancancel")]]))
    except:
        update.effective_message.reply_text("Failed To GBAN")
        return


def gban_btn(update, context):
    message = update.effective_message
    chat = update.effective_chat
    query = update.callback_query
    bot = context.bot
    match = re.match(r"gbanbtn_\((.+?)\)\((.+?)\)", query.data)

    if match:
        user_id = match.group(1)
        reason = match.group(2)
    try:
        user_chat = bot.get_chat(user_id)
    except:
        message.reply_test("Failed To Extract User Data!")
        return

    sql.gban_user(user_id, user_chat.username or user_chat.first_name, reason)

    start_time = time.time()
    datetime_fmt = "%H:%M - %d-%m-%Y"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    chats = get_user_com_chats(user_id)
    gbanned_chats = 0

    message.edit_text(
        "<b>Done! {} has been globally banned.</b>".format(mention_html(user_chat.id, user_chat.first_name)),
        parse_mode=ParseMode.HTML)
    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            bot.ban_chat_member(chat_id, user_id)
            gbanned_chats += 1
        except BadRequest as excp:
            if excp.message in GBAN_ERRORS:
                pass
            else:
                message.reply_text("Could not gban due to: {}".format(excp.message))
                if GBAN_LOGS:
                    bot.send_message(
                        GBAN_LOGS,
                        f"Could not gban due to {excp.message}",
                        parse_mode=ParseMode.HTML)
                else:
                    send_to_list(bot, SUDO_USERS + DEV_USERS,
                                 f"Could not gban due to: {excp.message}")
                sql.ungban_user(user_id)
                return
        except TelegramError:
            pass

    end_time = time.time()
    gban_time = round((end_time - start_time), 2)

    if gban_time > 60:
        gban_time = round((gban_time / 60), 2)
        message.reply_text(f"Done! This gban affected {gbanned_chats} chats, Took {gban_time} min")
    else:
        message.reply_text(f"Done! This gban affected {gbanned_chats} chats, Took {gban_time} sec")


def gbancancelbtn(update, context):
    message = update.effective_message
    message.edit_text("GBAN Request Declined")
    return


def ungban(update, context):
    message = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat
    user = update.effective_user
    args = context.args;
    bot = context.bot
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("You don't seem to be referring to a user.")
        return

    user_chat = bot.get_chat(user_id)
    if user_chat.type != 'private':
        message.reply_text("That's not a user!")
        return

    if not sql.is_user_gbanned(user_id):
        message.reply_text("This user is not gbanned!")
        return

    message.reply_text("I pardon {}, globally with a second chance.".format(user_chat.first_name))

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != 'private':
        chat_origin = "<b>{} ({})</b>\n".format(html.escape(chat.title), chat.id)
    else:
        chat_origin = "<b>{}</b>\n".format(chat.id)

    log_message = (
        f"#UNGBANNED\n"
        f"<b>Originated from:</b> {chat_origin}\n"
        f"<b>Targeted User:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Unbanned User:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>Unbanned User ID:</b> {user_chat.id}\n"
        f"<b>Event Stamp:</b> {current_time}")

    if GBAN_LOGS:
        try:
            log = bot.send_message(
                GBAN_LOGS, log_message, parse_mode=ParseMode.HTML)
        except BadRequest as excp:
            log = bot.send_message(
                GBAN_LOGS,
                log_message +
                "\n\nFormatting has been disabled due to an unexpected error.")
    else:
        send_to_list(bot, SUDO_USERS + DEV_USERS, log_message, html=True)

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
            if excp.message in UNGBAN_ERRORS:
                pass
            else:
                message.reply_text("Could not un-gban due to: {}".format(excp.message))
                if GBAN_LOGS:
                    bot.send_message(
                        GBAN_LOGS,
                        f"Could not un-gban due to: {excp.message}",
                        parse_mode=ParseMode.HTML)
                else:
                    bot.send_message(
                        OWNER_ID, f"Could not un-gban due to: {excp.message}")
                return
        except TelegramError:
            pass

    sql.ungban_user(user_id)

    if GBAN_LOGS:
        log.edit_text(
            log_message +
            f"\n<b>Chats affected:</b> {ungbanned_chats}",
            parse_mode=ParseMode.HTML)
    else:
        send_to_list(bot, SUDO_USERS + DEV_USERS,
                     "{} has been pardoned from gban!".format(mention_html(user_chat.id,
                                                                           user_chat.first_name)),
                     html=True)

    message.reply_text("{} has been un-gbanned".format(mention_html(user_chat.id, user_chat.first_name)),
                       parse_mode=ParseMode.HTML)
    end_time = time.time()
    ungban_time = round((end_time - start_time), 2)

    if ungban_time > 60:
        ungban_time = round((ungban_time / 60), 2)
        message.reply_text(
            f"Done! This Ungban affected {ungbanned_chats} chats, Took {ungban_time} min")
    else:
        message.reply_text(f"Done! This Ungban affected {ungbanned_chats} chats, Took {ungban_time} sec")


def gbanlist(update, context):
    banned_users = sql.get_gban_list()

    if not banned_users:
        update.effective_message.reply_text("There aren't any gbanned users! You're kinder than I expected...")
        return

    banfile = 'Screw these guys.\n'
    for user in banned_users:
        banfile += "[x] {} - {}\n".format(user["name"], user["user_id"])
        if user["reason"]:
            banfile += "Reason: {}\n".format(user["reason"])

    with BytesIO(str.encode(banfile)) as output:
        output.name = "gbanlist.txt"
        update.effective_message.reply_document(document=output, filename="gbanlist.txt",
                                                caption="Here is the list of currently gbanned users.")


def check_and_ban(update, user_id, should_message=True):
    chat = update.effective_chat
    message = update.effective_message

    if sql.is_user_gbanned(user_id):
        chat.kick_member(user_id)
        if should_message:
            userr = sql.get_gbanned_user(user_id)
            usrreason = userr.reason
            if not usrreason:
                usrreason = (chat.id, "No reason given")

            message.reply_text("*This user is gbanned and has been removed.*\nReason: `{}`".format(usrreason),
                               parse_mode=ParseMode.MARKDOWN)
            return


def enforce_gban(update, context):
    bot = context.bot
    # Not using @restrict handler to avoid spamming - just ignore if cant gban.
    if sql.does_chat_gban(update.effective_chat.id) and update.effective_chat.get_member(bot.id).can_restrict_members:
        user = update.effective_user  # type: Optional[User]
        chat = update.effective_chat  # type: Optional[Chat]
        msg = update.effective_message  # type: Optional[Message]

        if user and not is_user_admin(chat, user.id):
            check_and_ban(update, user.id)

        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                check_and_ban(update, mem.id)

        if msg.reply_to_message:
            user = msg.reply_to_message.from_user  # type: Optional[User]
            if user and not is_user_admin(chat, user.id):
                check_and_ban(update, user.id, should_message=False)


@user_admin
def gbanstat(update, context):
    args = context.args
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_gbans(update.effective_chat.id)
            update.effective_message.reply_text("I've enabled gbans in this group. This will help protect you "
                                                "from spammers, unsavoury characters, and the biggest trolls.")
        elif args[0].lower() in ["off", "no"]:
            sql.disable_gbans(update.effective_chat.id)
            update.effective_message.reply_text("I've disabled gbans in this group. GBans wont affect your users "
                                                "anymore. You'll be less protected from any trolls and spammers "
                                                "though!")
    else:
        update.effective_message.reply_text("Give me some arguments to choose a setting! on/off, yes/no!\n\n"
                                            "Your current setting is: {}\n"
                                            "When True, any gbans that happen will also happen in your group. "
                                            "When False, they won't, leaving you at the possible mercy of "
                                            "spammers.".format(sql.does_chat_gban(update.effective_chat.id)))


def clear_gbans(update, context):
    '''Check and remove deleted accounts from gbanlist.
    By @itzz_axel'''
    bot = context.bot
    banned = sql.get_gban_list()
    deleted = 0
    for user in banned:
        id = user["user_id"]
        time.sleep(0.1)  # Reduce floodwait
        try:
            acc = bot.get_chat(id)
            if not acc.first_name:
                deleted += 1
                sql.ungban_user(id)
        except BadRequest:
            deleted += 1
            sql.ungban_user(id)
    update.message.reply_text("Done! `{}` deleted accounts were removed " \
                              "from the gbanlist.".format(deleted), parse_mode=ParseMode.MARKDOWN)


def check_gbans(update, context):
    '''By @itzz_axel'''
    bot = context.bot
    banned = sql.get_gban_list()
    deleted = 0
    for user in banned:
        id = user["user_id"]
        time.sleep(0.1)  # Reduce floodwait
        try:
            acc = bot.get_chat(id)
            if not acc.first_name:
                deleted += 1
        except BadRequest:
            deleted += 1
    if deleted:
        update.message.reply_text("`{}` deleted accounts found in the gbanlist! " \
                                  "Run /cleangb to remove them from the database!".format(deleted),
                                  parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text("No deleted accounts in the gbanlist!")


def __stats__():
    return "{} gbanned users.".format(sql.num_gbanned_users())


def __user_info__(user_id):
    is_gbanned = sql.is_user_gbanned(user_id)

    text = "Globally blacklisted: <b>{}</b>"
    if is_gbanned:
        text = text.format("Yes")
        user = sql.get_gbanned_user(user_id)
        if user.reason:
            text += "\nReason: {}".format(html.escape(user.reason))
    else:
        text = text.format("No")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return "This chat is enforcing *gbans*: `{}`.".format(sql.does_chat_gban(chat_id))


__mod_name__ = "GLOBAL BANS"

GBAN_HANDLER = CommandHandler("gban", gban,
                              filters=CustomFilters.sudo_filter | CustomFilters.support_filter)
UNGBAN_HANDLER = CommandHandler("ungban", ungban,
                                filters=CustomFilters.sudo_filter | CustomFilters.support_filter)
GBAN_LIST = CommandHandler("gbanlist", gbanlist,
                           filters=CustomFilters.sudo_filter | CustomFilters.support_filter)

GBAN_STATUS = CommandHandler("gbanstat", gbanstat, filters=Filters.group)
CHECK_GBAN_HANDLER = CommandHandler("checkgb", check_gbans, filters=Filters.user(OWNER_ID))
CLEAN_GBAN_HANDLER = CommandHandler("cleangb", clear_gbans, filters=Filters.user(OWNER_ID))
GBANCANCEL = CallbackQueryHandler(gbancancelbtn, pattern=r"gbancancel")
GBANAPPROVAL = CallbackQueryHandler(gban_btn, pattern=r"gbanbtn_")

GBAN_ENFORCER = MessageHandler(Filters.all & Filters.group, enforce_gban)

dispatcher.add_handler(GBAN_HANDLER)
dispatcher.add_handler(UNGBAN_HANDLER)
dispatcher.add_handler(GBAN_LIST)
dispatcher.add_handler(GBAN_STATUS)
dispatcher.add_handler(CHECK_GBAN_HANDLER)
dispatcher.add_handler(CLEAN_GBAN_HANDLER)
dispatcher.add_handler(GBANCANCEL)
dispatcher.add_handler(GBANAPPROVAL)

if STRICT_GBAN:  # enforce GBANS if this is set
    dispatcher.add_handler(GBAN_ENFORCER, GBAN_ENFORCE_GROUP)
