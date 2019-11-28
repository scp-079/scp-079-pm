# SCP-079-PM - Everyone can have their own Telegram private chat bot
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-PM.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup, Message

from .. import glovar
from .. functions.deliver import clear_data, get_guest, list_page_ids, recall_messages
from ..functions.etc import bold, button_data, code, general_link, get_callback_data, get_command_type, get_int, lang
from ..functions.etc import mention_id, thread
from ..functions.file import save
from ..functions.filters import from_user, host_chat, test_group
from ..functions.ids import add_id, remove_id
from ..functions.telegram import delete_messages, edit_message_reply_markup, edit_message_text, get_start
from ..functions.telegram import resolve_username, send_message
from ..functions.user import forgive_user, unblock_user

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.command(["block"], glovar.prefix)
                   & host_chat
                   & from_user)
def block(client: Client, message: Message) -> bool:
    # Block a user
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        _, cid = get_guest(message)
        cid = cid or get_int(get_command_type(message))

        # Block the user
        if cid:
            if cid not in glovar.blacklist_ids:
                add_id(cid, 0, "blacklist")
                # When add someone to blacklist, delete all messages in this guest's chat
                if glovar.message_ids.get(cid) and glovar.message_ids[cid]["host"]:
                    thread(delete_messages, (client, cid, glovar.message_ids[cid]["host"]))

                if glovar.message_ids.get(cid) and glovar.message_ids[cid]["guest"]:
                    thread(delete_messages, (client, cid, glovar.message_ids[cid]["guest"]))

                remove_id(cid, mid, "chat_all")
                text = (f"{lang('user_id')}{lang('colon')}{code(cid)}\n"
                        f"{lang('action')}{lang('colon')}{code(lang('action_block'))}\n"
                        f"{lang('status')}{lang('colon')}{code(lang('status_succeed'))}\n")
            else:
                text = (f"{lang('user_id')}{lang('colon')}{code(cid)}\n"
                        f"{lang('action')}{lang('colon')}{code(lang('action_block'))}\n"
                        f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                        f"{lang('reason')}{lang('colon')}{code(lang('reason_blocked'))}\n")

            if glovar.host_id > 0:
                unblock_link = general_link("/unblock", get_start(client, f"unblock_{cid}"))
                text += f"{lang('action_unblock')}{lang('colon')}{unblock_link}\n"
        else:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_block'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                    f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")

        # Admin info text
        if glovar.host_id < 0:
            text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

        # Send the report message
        thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Block error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.private & Filters.command(["clear"], glovar.prefix)
                   & host_chat
                   & from_user)
def clear(client: Client, message: Message) -> bool:
    # Clear stored data
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        command_type = get_command_type(message)

        # Check the command
        if not command_type:
            text = (f"{lang('action')}{lang('colon')}{code(lang('clear'))}\n"
                    f"{lang('description')}{lang('colon')}{code(lang('description_choose_clear'))}\n")
            data_blacklist = button_data("clear", "blacklist", 0)
            data_flood = button_data("clear", "flood", 0)
            data_message = button_data("clear", "message", 0)
            data_cancel = button_data("cancel", None, None)
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=lang("blacklist_ids"),
                            callback_data=data_blacklist
                        ),
                        InlineKeyboardButton(
                            text=lang("flood_ids"),
                            callback_data=data_flood
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=lang("message_ids"),
                            callback_data=data_message
                        ),
                        InlineKeyboardButton(
                            text=lang("cancel"),
                            callback_data=data_cancel
                        )
                    ]
                ]
            )
        elif command_type in {"blacklist", "messages"}:
            text = clear_data(command_type)
            markup = None
        else:
            text = (f"{lang('action')}{lang('colon')}{lang('clear')}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                    f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")
            markup = None

        # Admin info text
        if glovar.host_id < 0:
            text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

        # Send the report message
        thread(send_message, (client, hid, text, mid, markup))

        return True
    except Exception as e:
        logger.warning(f"Clear error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.command(["direct"], glovar.prefix)
                   & host_chat
                   & from_user)
def direct_chat(client: Client, message: Message) -> bool:
    # Start a direct chat
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        _, cid = get_guest(message)

        # Assign the direct chat
        if cid:
            if cid not in glovar.blacklist_ids:
                glovar.direct_chat = cid
                text = (f"{lang('user_id')}{lang('colon')}{code(cid)}\n"
                        f"{lang('action')}{lang('colon')}{code(lang('action_direct'))}\n"
                        f"{lang('status')}{lang('colon')}{code(lang('status_succeed'))}\n"
                        f"{lang('action_leave')}{lang('colon')}/leave\n")
            else:
                text = (f"{lang('user_id')}{lang('colon')}{code(cid)}\n"
                        f"{lang('action')}{lang('colon')}{code(lang('action_direct'))}\n"
                        f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                        f"{lang('reason')}{lang('colon')}{code(lang('reason_blacklist'))}\n")

                if glovar.host_id > 0:
                    unblock_link = general_link("/unblock", get_start(client, f"unblock_{cid}"))
                    text += f"{lang('action_unblock')}{lang('colon')}{unblock_link}\n"
        else:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_direct'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                    f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")

        # Admin info text
        if glovar.host_id < 0:
            text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

        # Send the report message
        thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Direct chat error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.command(["forgive"], glovar.prefix)
                   & host_chat
                   & from_user)
def forgive(client: Client, message: Message) -> bool:
    # Forgive a user
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        _, uid = get_guest(message)
        command_type = get_command_type(message)

        # Get the user's id
        if not uid and command_type:
            uid = get_int(command_type)

        # Unblock the user
        if uid:
            forgive_user(client, uid, mid, aid)
        else:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_forgive'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                    f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")
            # Admin info text
            if glovar.host_id < 0:
                text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

            # Send the report message
            thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Forgive error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.command(["leave"], glovar.prefix)
                   & host_chat
                   & from_user)
def leave_chat(client: Client, message: Message) -> bool:
    # Leave the direct chat
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        cid = glovar.direct_chat
        mid = message.message_id

        if cid:
            glovar.direct_chat = 0
            text = (f"{lang('user_id')}{lang('colon')}{code(cid)}\n"
                    f"{lang('action')}{lang('colon')}{code(lang('action_leave'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_succeed'))}\n")
        else:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_leave'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                    f"{lang('reason')}{lang('colon')}{code(lang('reason_no_direct'))}\n")

        # Admin info text
        if glovar.host_id < 0:
            text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

        # Send the report message
        thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Leave chat error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.command(["list", "ls"], glovar.prefix)
                   & host_chat
                   & from_user)
def list_ids(client: Client, message: Message) -> bool:
    # List IDs
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        action_type = get_command_type(message)

        # Get the text and markup
        text, markup = list_page_ids(action_type, 1, aid)

        # Send the report message
        thread(send_message, (client, hid, text, mid, markup))

        return True
    except Exception as e:
        logger.warning(f"List ids error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.command(["mention"], glovar.prefix)
                   & host_chat
                   & from_user)
def mention(client: Client, message: Message) -> bool:
    # Force mention a user
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        _, uid = get_guest(message)
        command_type = get_command_type(message)

        # Get the user's ID
        if uid:
            uid = uid
        elif command_type:
            uid = get_int(command_type)
            if not uid:
                the_type, the_id = resolve_username(client, command_type, False)
                if the_type == "user":
                    uid = the_id

        # Mention the user
        if uid:
            text = (f"{lang('user_id')}{lang('colon')}{mention_id(uid)}\n"
                    f"{lang('action')}{lang('colon')}{code(lang('action_mention'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_succeed'))}\n")
        else:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_mention'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                    f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")

        # Admin info text
        if glovar.host_id < 0:
            text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

        # Send the report message
        thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Mention error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.command(["now"], glovar.prefix)
                   & host_chat
                   & from_user)
def now_chat(client: Client, message: Message) -> bool:
    # Check direct chat status
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        cid = glovar.direct_chat

        # Check direct chat
        if cid:
            text = (f"{lang('user_id')}{lang('colon')}{code(cid)}\n"
                    f"{lang('action')}{lang('colon')}{code(lang('action_now'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_succeed'))}\n"
                    f"{lang('leave_chat')}{lang('colon')}/leave\n")
        else:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_now'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                    f"{lang('reason')}{lang('colon')}{code(lang('reason_no_direct'))}\n")

        # Admin info text
        if glovar.host_id < 0:
            text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

        # Send the report message
        thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Now chat error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.command(["page"], glovar.prefix)
                   & host_chat
                   & from_user)
def page_command(client: Client, message: Message) -> bool:
    # Change page
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        the_type = get_command_type(message)
        r_message = message.reply_to_message
        rid = r_message and r_message.message_id

        # Generate the report message's text
        text = f"{lang('action')}{lang('colon')}{code(lang('action_page'))}\n"

        # Proceed
        if the_type in {"previous", "next"} and r_message and r_message.from_user.is_self:
            callback_data_list = get_callback_data(r_message)
            i = (lambda x: 0 if x == "previous" else -1)(the_type)
            if callback_data_list and callback_data_list[i]["a"] == "list":
                action_type = callback_data_list[i]["t"]
                page = callback_data_list[i]["d"]
                page_text, markup = list_page_ids(action_type, page, aid)
                thread(edit_message_text, (client, hid, rid, page_text, markup))
                text += f"{lang('status')}{lang('colon')}{code(lang('status_succeed'))}\n"
            else:
                text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                         f"{lang('reason')}{lang('colon')}{code(lang('command_reply'))}\n")
        else:
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")

        # Admin info text
        if glovar.host_id < 0:
            text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

        # Send the report message
        thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Page command error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.private & Filters.command(["ping"], glovar.prefix)
                   & host_chat
                   & from_user)
def ping(client: Client, message: Message) -> bool:
    # Ping
    try:
        hid = message.from_user.id
        text = code("Pong!")
        thread(send_message, (client, hid, text))

        return True
    except Exception as e:
        logger.warning(f"Ping error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.command(["recall"], glovar.prefix)
                   & host_chat
                   & from_user)
def recall(client: Client, message: Message) -> bool:
    # Recall messages
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        recall_mid, cid = get_guest(message)
        command_type = get_command_type(message)

        # Check the chat ID
        if cid:
            # Base text
            text = (f"{lang('chat_id')}{lang('colon')}{code(cid)}\n"
                    f"{lang('action')}{lang('colon')}{code(lang('action_recall'))}\n")

            # Check the command
            if not command_type:
                text += f"{lang('description')}{lang('colon')}{code(lang('description_choose_recall'))}\n"
                data_host = button_data("recall", "host", str(cid))
                data_all = button_data("recall", "all", str(cid))
                data_cancel = button_data("cancel", None, None)
                markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=lang("message_host"),
                                callback_data=data_host
                            ),
                            InlineKeyboardButton(
                                text=lang("message_all"),
                                callback_data=data_all
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text=lang("cancel"),
                                callback_data=data_cancel
                            )
                        ]
                    ]
                )
            elif command_type in {"all", "host", "single"}:
                # If the host want to recall single message, bot should found which message to recall
                if command_type == "single" and not recall_mid:
                    # Get the message's id from message's inline button's data
                    callback_data_list = get_callback_data(message.reply_to_message)

                    if (callback_data_list
                            and callback_data_list[0]["a"] == "recall"
                            and callback_data_list[0]["t"] == "single"):
                        recall_mid = callback_data_list[0]["d"]

                        # Edit the origin report message, delete the reply markup
                        thread(edit_message_reply_markup, (client, hid, message.reply_to_message.message_id, None))
                    # If the data cannot be found, send a error message
                    else:
                        text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                                 f"{lang('reason')}{lang('colon')}{code(lang('command_origin'))}\n")
                        markup = None

                        # Admin info text
                        if glovar.host_id < 0:
                            text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

                        thread(send_message, (client, hid, text, mid, markup))

                        return True

                text = recall_messages(client, cid, command_type, recall_mid)
                markup = None
            else:
                text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                         f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")
                markup = None
        else:
            text = (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                    f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")
            markup = None

        # Admin info text
        if glovar.host_id < 0:
            text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

        # Send the report message
        thread(send_message, (client, hid, text, mid, markup))

        return True
    except Exception as e:
        logger.warning(f"Recall error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.private & Filters.command(["start"], glovar.prefix)
                   & from_user)
def start(client: Client, message: Message) -> bool:
    # Send welcome message
    glovar.locks["message"].acquire()
    try:
        # Basic data
        cid = message.chat.id
        uid = message.from_user.id
        mid = message.message_id
        command_type = get_command_type(message)

        # Check the command
        if cid == glovar.host_id and command_type and "_" in command_type:
            para_list = command_type.split("_")
            if len(para_list) == 2:
                para_action = para_list[0]
                para_data = para_list[1]
                if para_action == "unblock":
                    cid = get_int(para_data)
                    unblock_user(client, cid, mid, uid)
                elif para_action == "forgive":
                    cid = get_int(para_data)
                    forgive_user(client, cid, mid, uid)
        else:
            # Host
            if cid == glovar.host_id:
                link_text = general_link(lang("this_page"), "https://scp-079.org/pm/")
                text = lang("start_host").format(link_text)

            # Guest
            elif uid not in glovar.blacklist_ids and uid not in glovar.flood_ids["users"]:
                link_text = general_link(lang("description"), "https://scp-079.org/pm/")
                text = lang("start_guest").format(code(glovar.host_name), link_text)

                # Show status text
                if glovar.status and glovar.host_id > 0:
                    text += f"{lang('user_status')}{lang('colon')}{code(glovar.status)}\n"
                elif glovar.status:
                    text += "\n" + glovar.status

            # Limited user
            else:
                text = ""

            # Send the report message
            thread(send_message, (client, cid, text))

        return True
    except Exception as e:
        logger.warning(f"Start error: {e}", exc_info=True)
    finally:
        glovar.locks["message"].release()

    return False


@Client.on_message(Filters.incoming & Filters.command(["status"], glovar.prefix)
                   & from_user)
def status(client: Client, message: Message) -> bool:
    # Set status
    try:
        # Basic data
        hid = glovar.host_id
        cid = message.chat.id
        aid = message.from_user.id
        mid = message.message_id
        command_type = get_command_type(message)

        if cid == hid:
            # Check the command
            if command_type:
                if command_type == "off":
                    glovar.status = ""
                    text = (f"{lang('action')}{lang('colon')}{code(lang('action_status_set'))}\n"
                            f"{lang('status')}{lang('colon')}{code(lang('reason_none'))}\n")
                else:
                    glovar.status = command_type
                    text = (f"{lang('action')}{lang('colon')}{code(lang('action_status_set'))}\n"
                            f"{lang('status')}{lang('colon')}{code(glovar.status)}\n")

                save("status")
            else:
                text = f"{lang('action')}{lang('colon')}{code(lang('action_status_show'))}\n"
                if glovar.status:
                    text += f"{lang('status')}{lang('colon')}{code(glovar.status)}\n"
                else:
                    text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                             f"{lang('reason')}{lang('colon')}{code(lang('reason_none'))}\n")

            # Admin info text
            if glovar.host_id < 0:
                text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"
        else:
            # Check the ban status

            # Text prefix
            text = f"{lang('action')}{lang('colon')}{code(lang('action_check'))}\n"

            if cid in glovar.bad_ids["users"]:
                text += (f"{lang('result')}{lang('colon')}{code(lang('result_yes'))}\n"
                         f"{lang('suggestion')}{lang('colon')}" + "-" * 24 + "\n\n")
                suggestion_list = lang("suggestion_yes").format(cid).split("\n\n")
                text += "\n\n".join(code(suggestion) for suggestion in suggestion_list) + "\n"
            else:
                text += (f"{lang('result')}{lang('colon')}{code(lang('result_no'))}\n"
                         f"{lang('suggestion')}{lang('colon')}{code(lang('suggestion_no'))}\n")

        # Send the report message
        thread(send_message, (client, cid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Status error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.command(["unblock"], glovar.prefix)
                   & from_user & host_chat)
def unblock(client: Client, message: Message) -> bool:
    # Unblock a user
    try:
        # Basic data
        hid = glovar.host_id
        aid = message.from_user.id
        mid = message.message_id
        _, uid = get_guest(message)
        command_type = get_command_type(message)

        # Get the user's id
        if not uid and command_type:
            uid = get_int(command_type)

        # Unblock the user
        if uid:
            unblock_user(client, uid, mid, aid)
        else:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_unblock'))}\n"
                    f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                    f"{lang('reason')}{lang('colon')}{code(lang('command_usage'))}\n")

            # Admin info text
            if glovar.host_id < 0:
                text += f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n"

            # Send the report message
            thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Unblock error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.group & Filters.command(["version"], glovar.prefix)
                   & test_group & from_user)
def version(client: Client, message: Message) -> bool:
    # Check the program's version
    try:
        cid = message.chat.id
        aid = message.from_user.id
        mid = message.message_id
        text = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n\n"
                f"{lang('version')}{lang('colon')}{bold(glovar.version)}\n")
        thread(send_message, (client, cid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Version error: {e}", exc_info=True)

    return False
