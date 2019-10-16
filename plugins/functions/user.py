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

from pyrogram import Client

from .. import glovar
from .etc import code, lang, thread, user_mention
from .ids import remove_id
from .telegram import send_message

# Enable logging
logger = logging.getLogger(__name__)


def forgive_user(client: Client, uid: int, mid: int) -> bool:
    # Forgive the flood user
    try:
        text = (f"{lang('user_id')}{lang('colon')}{user_mention(uid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_forgive'))}\n")

        if uid in glovar.flood_ids["users"]:
            # Remove the flood status
            remove_id(uid, 0, "flood")
            text += f"{lang('status')}{lang('colon')}{code(lang('status_succeed'))}\n"

            # Send the report message to the guest
            guest_text = f"{lang('description_forgive')}\n"
            thread(send_message, (client, uid, guest_text))
        else:
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('reason_not_limited'))}\n")

        thread(send_message, (client, glovar.host_id, text, mid))
    except Exception as e:
        logger.warning(f"Forgive user error: {e}", exc_info=True)

    return False


def unblock_user(client: Client, uid: int, mid: int) -> bool:
    # Unblock a user
    try:
        text = (f"{lang('user_id')}{lang('colon')}{user_mention(uid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_unblock'))}\n")

        if uid in glovar.blacklist_ids:
            remove_id(uid, 0, "blacklist")
            text += f"{lang('status')}{lang('colon')}{code(lang('status_succeed'))}\n"
        else:
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('reason_not_blocked'))}\n")

        thread(send_message, (client, glovar.host_id, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Unblock user error: {e}", exc_info=True)

    return False
