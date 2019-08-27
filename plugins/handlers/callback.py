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
import json

from pyrogram import Client, CallbackQuery

from .. import glovar
from ..functions.etc import thread
from ..functions.deliver import clear_data, recall_messages
from ..functions.telegram import answer_callback, edit_message_text

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_callback_query()
def answer(client: Client, callback_query: CallbackQuery) -> bool:
    # Answer the callback query
    try:
        uid = callback_query.from_user.id
        hid = glovar.host_id
        # Check permission
        if uid == hid:
            mid = callback_query.message.message_id
            callback_data = json.loads(callback_query.data)
            # If action is recall
            if callback_data["a"] == "recall":
                cid = int(callback_query.message.text.partition("\n")[0].partition("ID")[2][1:])
                text = recall_messages(client, cid, callback_data["t"], callback_data["d"])
                markup = None
                thread(edit_message_text, (client, hid, mid, text, markup))
            # Clear all stored data
            elif callback_data["a"] == "clear":
                text = clear_data(callback_data["t"])
                markup = None
                thread(edit_message_text, (client, hid, mid, text, markup))

            thread(answer_callback, (client, callback_query.id, ""))

        return True
    except Exception as e:
        logger.warning(f"Answer callback error: {e}", exc_info=True)

    return False
