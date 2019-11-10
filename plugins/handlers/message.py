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

from pyrogram import Client, Filters, Message

from .. import glovar
from ..functions.etc import code, bold, general_link, lang, thread
from ..functions.deliver import deliver_guest_message, deliver_host_message, get_guest, send_message
from ..functions.filters import exchange_channel, from_user, hide_channel, host_chat, is_limited_user, limited_user
from ..functions.ids import add_id, count_id
from ..functions.receive import receive_rollback, receive_text_data
from ..functions.timers import backup_files
from ..functions.telegram import get_start

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.private & Filters.incoming
                   & from_user & ~host_chat & ~limited_user, group=1)
def count(client: Client, message: Message) -> bool:
    # Count messages sent by guest
    glovar.locks["count"].acquire()
    try:
        # Count user's messages
        counts = count_id(message)

        # Check the flood status
        if counts < glovar.flood_limit:
            return True

        uid = message.from_user.id
        add_id(uid, 0, "flood")

        # Send the report message to the guest
        text = lang("description_flood").format(bold(glovar.flood_ban))
        thread(send_message, (client, uid, text))

        # Send the report message to the host
        forgive_link = general_link("/forgive", get_start(client, f"forgive_{uid}"))
        text = (f"{lang('user_id')}{lang('colon')}{code(uid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_limit'))}\n"
                f"{lang('action_forgive')}{lang('colon')}{forgive_link}\n")
        thread(send_message, (client, glovar.host_id, text))

        return True
    except Exception as e:
        logger.warning(f"Count error: {e}", exc_info=True)
    finally:
        glovar.locks["count"].release()

    return False


@Client.on_message(Filters.private & Filters.incoming & ~Filters.command(glovar.all_commands, glovar.prefix)
                   & from_user & host_chat)
def deliver_to_guest(client: Client, message: Message) -> bool:
    # Deliver messages to guest
    glovar.locks["message"].acquire()
    try:
        # Basic data
        hid = message.chat.id
        mid = message.message_id
        _, cid = get_guest(message)

        # Deliver the message to guest
        if cid:
            thread(deliver_host_message, (client, message, cid))
        elif glovar.direct_chat:
            thread(deliver_host_message, (client, message, glovar.direct_chat))
        else:
            if not message.forward_date:
                text = (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                        f"{lang('description')}{lang('colon')}{code(lang('description_reply'))}\n")
            else:
                text = (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                        f"{lang('description')}{lang('colon')}{code(lang('description_direct'))}\n")

            thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Deliver to guest error: {e}", exc_info=True)
    finally:
        glovar.locks["message"].release()

    return False


@Client.on_message(Filters.private & Filters.incoming & ~Filters.command(glovar.all_commands, glovar.prefix)
                   & from_user & ~host_chat & ~limited_user, group=0)
def deliver_to_host(client: Client, message: Message) -> bool:
    # Deliver messages to host
    glovar.locks["message"].acquire()
    try:
        # Check the limit status
        if is_limited_user(None, message):
            return True
        
        deliver_guest_message(client, message)

        return True
    except Exception as e:
        logger.warning(f"Deliver to host error: {e}", exc_info=True)
    finally:
        glovar.locks["message"].release()

    return False


@Client.on_message(Filters.incoming & Filters.channel & ~Filters.command(glovar.all_commands, glovar.prefix)
                   & hide_channel, group=-1)
def exchange_emergency(client: Client, message: Message) -> bool:
    # Sent emergency channel transfer request
    try:
        # Read basic information
        data = receive_text_data(message)

        if not data:
            return True

        sender = data["from"]
        receivers = data["to"]
        action = data["action"]
        action_type = data["type"]
        data = data["data"]

        if "EMERGENCY" not in receivers:
            return True

        if action != "backup":
            return True

        if action_type != "hide":
            return True

        if data is True:
            glovar.should_hide = data
        elif data is False and sender == "MANAGE":
            glovar.should_hide = data

        project_text = general_link(glovar.project_name, glovar.project_link)
        hide_text = (lambda x: lang("enabled") if x else "disabled")(glovar.should_hide)
        text = (f"{lang('project')}{lang('colon')}{project_text}\n"
                f"{lang('action')}{lang('colon')}{code(lang('transfer_channel'))}\n"
                f"{lang('emergency_channel')}{lang('colon')}{code(hide_text)}\n")
        thread(send_message, (client, glovar.debug_channel_id, text))

        return True
    except Exception as e:
        logger.warning(f"Exchange emergency error: {e}", exc_info=True)

    return False


@Client.on_message(Filters.incoming & Filters.channel & ~Filters.command(glovar.all_commands, glovar.prefix)
                   & exchange_channel)
def process_data(client: Client, message: Message) -> bool:
    # Process the data in exchange channel
    glovar.locks["receive"].acquire()
    try:
        data = receive_text_data(message)

        if not data:
            return True

        sender = data["from"]
        receivers = data["to"]
        action = data["action"]
        action_type = data["type"]
        data = data["data"]

        # This will look awkward,
        # seems like it can be simplified,
        # but this is to ensure that the permissions are clear,
        # so it is intentionally written like this
        if glovar.sender in receivers:

            if sender == "MANAGE":

                if action == "backup":
                    if action_type == "now":
                        thread(backup_files, (client,))
                    elif action_type == "rollback":
                        receive_rollback(client, message, data)

        return True
    except Exception as e:
        logger.warning(f"Process data error: {e}", exc_info=True)
    finally:
        glovar.locks["receive"].release()

    return False
