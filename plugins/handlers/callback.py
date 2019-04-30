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

from pyrogram import Client

from .. import glovar
from ..functions.etc import code, thread
from ..functions.file import save
from ..functions.ids import init_id, remove_id
from ..functions.telegram import answer_callback, delete_messages, edit_message_text

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_callback_query()
def answer(client, callback_query):
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
                init_id(cid)
                # Recall single message
                if callback_data["t"] == "single":
                    recall_mid = int(callback_data["d"])
                    thread(delete_messages, (client, cid, [recall_mid]))
                    text = (f"发送至 ID：[{cid}](tg://user?id={cid})\n"
                            f"状态：{code('已撤回')}")
                    remove_id(cid, mid, "host")
                # Recall all host's messages
                elif callback_data["t"] == "host":
                    if glovar.message_ids[cid]["host"]:
                        thread(delete_messages, (client, cid, glovar.message_ids[cid]["host"]))
                        text = (f"对话 ID：[{cid}](tg://user?id={cid})\n"
                                f"状态：{code('已撤回由您发送的全部消息')}")
                        remove_id(cid, mid, "chat_host")
                    else:
                        text = (f"对话 ID：[{cid}](tg://user?id={cid})\n"
                                f"状态：{code('没有可撤回的消息')}")
                # Recall all messages in a guest's chat
                else:
                    if glovar.message_ids[cid]["host"] or glovar.message_ids[cid]["guest"]:
                        if glovar.message_ids[cid]["host"]:
                            thread(delete_messages, (client, cid, glovar.message_ids[cid]["host"]))

                        if glovar.message_ids[cid]["guest"]:
                            thread(delete_messages, (client, cid, glovar.message_ids[cid]["guest"]))

                        text = (f"对话 ID：[{cid}](tg://user?id={cid})\n"
                                f"状态：{code('已撤回全部消息')}")
                        remove_id(cid, mid, "chat_all")
                    else:
                        text = (f"对话 ID：[{cid}](tg://user?id={cid})\n"
                                f"状态：{code('没有可撤回的消息')}")

                markup = None
                thread(edit_message_text, (client, hid, mid, text, markup))
            # Clear all stored data
            elif callback_data["a"] == "clear":
                if callback_data["t"] == "messages":
                    glovar.message_ids = {}
                    save("message_ids")
                    glovar.reply_ids = {
                        "g2h": {},
                        "h2g": {}
                    }
                    save("reply_ids")
                    text = f"已清空：{code('消息 ID')}"
                else:
                    glovar.blacklist_ids = set()
                    save("blacklist_ids")
                    text = f"已清空：{code('黑名单')}"

                markup = None
                thread(edit_message_text, (client, hid, mid, text, markup))

            thread(answer_callback, (client, callback_query.id, ""))
    except Exception as e:
        logger.warning(f"Answer callback error: {e}", exc_info=True)
