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


def unblock_user(client: Client, hid: int, cid: int, mid: int) -> bool:
    # Unblock a user
    try:
        text = (f"{lang('user_id')}{lang('colon')}{user_mention(cid)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('action_unblock'))}\n")

        if cid in glovar.blacklist_ids:
            remove_id(cid, 0, "blacklist")
            text += f"{lang('status')}{lang('colon')}{code(lang('status_success'))}\n"
        else:
            text += (f"{lang('status')}{lang('colon')}{code(lang('status_failed'))}\n"
                     f"{lang('reason')}{lang('colon')}{code(lang('reason_not_blocked'))}\n")

        thread(send_message, (client, hid, text, mid))

        return True
    except Exception as e:
        logger.warning(f"Unblock user error: {e}", exc_info=True)

    return False
