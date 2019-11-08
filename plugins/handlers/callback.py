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
from ..functions.etc import get_int, thread
from ..functions.deliver import clear_data, list_page_ids, recall_messages
from ..functions.telegram import answer_callback, edit_message_text

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_callback_query()
def answer(client: Client, callback_query: CallbackQuery) -> bool:
    # Answer the callback query
    try:
        # Basic data
        cid = glovar.host_id
        uid = callback_query.from_user.id
        mid = callback_query.message.message_id
        callback_data = json.loads(callback_query.data)
        action = callback_data["a"]
        action_type = callback_data["t"]
        data = callback_data["d"]

        # Check permission
        if cid and uid != cid:
            return True

        # Clear all stored data
        if action == "clear":
            text = clear_data(callback_data["t"])
            markup = None
            thread(edit_message_text, (client, cid, mid, text, markup))

        # List
        if action == "list":
            page = data
            text, markup = list_page_ids(action_type, page)
            edit_message_text(client, cid, mid, text, markup)

        # Recall messages
        if action == "recall":
            cid = get_int(callback_query.message.text.partition("\n")[0].partition("ID")[2][1:])
            text = recall_messages(client, cid, callback_data["t"], callback_data["d"])
            markup = None
            thread(edit_message_text, (client, cid, mid, text, markup))

        thread(answer_callback, (client, callback_query.id, ""))

        return True
    except Exception as e:
        logger.warning(f"Answer callback error: {e}", exc_info=True)

    return False
