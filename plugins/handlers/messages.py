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

from pyrogram import Client, Filters

from .. import glovar
from ..functions.etc import thread
from ..functions.deliver import deliver_guest_message, deliver_host_message, send_message
from ..functions.filters import host_chat, limited_user
from ..functions.ids import add_id, count_id

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.private & Filters.incoming & host_chat
                   & ~Filters.command(glovar.all_commands, glovar.prefix))
def deliver_to_guest(client, message):
    try:
        hid = message.chat.id
        mid = message.message_id
        r_message = message.reply_to_message
        if r_message:
            if (r_message.from_user.is_self
                    and "ID" in message.reply_to_message.text
                    and len(message.reply_to_message.text.split("\n"))):
                thread(deliver_host_message, (client, message))
            else:
                text = "如需回复某人，请回复某条包含该用户 ID 的汇报消息"
                thread(send_message, (client, hid, text, mid))
        else:
            text = "如需回复某人，请回复某条包含该用户 ID 的汇报消息"
            thread(send_message, (client, hid, text, mid))
    except Exception as e:
        logger.warning(f"Deliver to guest error: {e}", exc_info=True)


@Client.on_message(Filters.private & Filters.incoming & ~host_chat & ~limited_user
                   & ~Filters.command(glovar.all_commands, glovar.prefix), group=0)
def deliver_to_host(client, message):
    try:
        thread(deliver_guest_message, (client, message))
    except Exception as e:
        logger.warning(f"Deliver to host error: {e}", exc_info=True)


@Client.on_message(Filters.private & Filters.incoming & ~host_chat & ~limited_user
                   & ~Filters.command(glovar.all_commands, glovar.prefix), group=1)
def count(client, message):
    try:
        cid = message.from_user.id
        counts = count_id(cid)
        if counts == 30:
            add_id(cid, 0, "flood")
            text = "您发送的消息过于频繁，请 15 分钟后重试\n期间机器人将对您的消息不做任何转发和应答"
            thread(send_message, (client, cid, text))
    except Exception as e:
        logger.warning(f"Deliver from error: {e}", exc_info=True)
