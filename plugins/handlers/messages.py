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
from ..functions.deliver import deliver_message_from, deliver_message_to, send_message
from ..functions.ids import add_id, count_id

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.private & Filters.incoming & ~Filters.command(commands=glovar.available_commands,
                                                                         prefix=glovar.prefix), group=-2)
def deliver_from(client, message):
    try:
        cid = message.chat.id
        if cid != glovar.creator_id and cid not in glovar.blacklist_ids and cid not in glovar.flood_ids["users"]:
            thread(deliver_message_from, (client, message))
    except Exception as e:
        logger.warning(f"Deliver from error: {e}", exc_info=True)


@Client.on_message(Filters.private & Filters.incoming & ~Filters.command(commands=glovar.available_commands,
                                                                         prefix=glovar.prefix), group=1)
def deliver_to(client, message):
    try:
        aid = message.chat.id
        if aid == glovar.creator_id:
            mid = message.message_id
            if message.reply_to_message:
                rid = message.reply_to_message.from_user.id
                if rid == glovar.me_id and "ID" in message.reply_to_message.text:
                    thread(deliver_message_to, (client, message))
                else:
                    text = "如需回复某人，请回复某条包含该用户 id 的汇报消息"
                    thread(send_message, (client, aid, text, mid))
            else:
                text = "如需回复某人，请回复某条包含该用户 id 的汇报消息"
                thread(send_message, (client, aid, text, mid))
    except Exception as e:
        logger.warning(f"Deliver from error: {e}", exc_info=True)


@Client.on_message(Filters.private & Filters.incoming & ~Filters.command(commands=glovar.available_commands,
                                                                         prefix=glovar.prefix), group=0)
def count(client, message):
    try:
        cid = message.from_user.id
        if cid != glovar.creator_id and cid not in glovar.blacklist_ids and cid not in glovar.flood_ids["users"]:
            counts = count_id(cid)
            if counts == 30:
                add_id(cid, 0, "flood")
                text = "您发送的消息过于频繁，请 15 分钟后重试\n期间机器人将对您的消息不做任何转发和应答"
                thread(send_message, (client, cid, text))
    except Exception as e:
        logger.warning(f"Deliver from error: {e}", exc_info=True)
