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
from time import sleep

from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, UserIsBlocked

from .. import glovar
from .etc import bytes_data, code, thread
from .telegram import send_message

# Enable logging
logger = logging.getLogger(__name__)


def deliver_message_from(client, message):
    try:
        aid = glovar.creator_id
        cid = message.chat.id
        mid = message.message_id
        try:
            m = client.forward_messages(
                chat_id=aid,
                from_chat_id=cid,
                message_ids=mid,
                disable_notification=True,
                as_copy=True
            )
        except FloodWait as e:
            sleep(e.x + 1)
            m = client.forward_messages(
                chat_id=aid,
                from_chat_id=cid,
                message_ids=mid,
                disable_notification=True,
                as_copy=True
            )
        except UserIsBlocked:
            deliver_fail(client, cid, mid)
            return False
        except Exception as e:
            logger.warning(f"Forward message error: {e}")
            return False

        text = (f"用户 ID：{code(cid)}\n"
                f"昵称：[{message.from_user.first_name}](tg://user?id={cid})")
        mid = m.message_id
        thread(send_message, (client, aid, text, mid))
    except Exception as e:
        logger.warning(f"Deliver message From error: {e}", exc_info=True)


def deliver_message_to(client, message):
    try:
        r_message = message.reply_to_message
        cid = int(r_message.text.partition("\n")[0].partition("ID")[2][1:])
        aid = glovar.creator_id
        mid = message.message_id
        try:
            m = client.forward_messages(
                chat_id=cid,
                from_chat_id=aid,
                message_ids=mid,
                disable_notification=True,
                as_copy=True
            )
        except FloodWait as e:
            sleep(e.x + 1)
            m = client.forward_messages(
                chat_id=cid,
                from_chat_id=aid,
                message_ids=mid,
                disable_notification=True,
                as_copy=True
            )
        except UserIsBlocked:
            deliver_fail(client, aid, mid)
            return False
        except Exception as e:
            logger.warning(f"Forward message error: {e}")
            return False

        text = (f"发送至 ID：[{cid}](tg://user?id={cid})\n"
                f"状态：{code('已发送')}")
        forward_mid = m.message_id
        data = bytes_data("recall", "single", str(forward_mid))
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "撤回",
                        callback_data=data
                    )
                ]
            ]
        )
        thread(send_message, (client, aid, text, mid, markup))
    except Exception as e:
        logger.warning(f"Deliver message To error: {e}", exc_info=True)


def deliver_fail(client, cid: int, mid: int):
    try:
        text = "发送失败，对方已停用机器人"
        thread(send_message, (client, cid, text, mid))
    except Exception as e:
        logger.warning(f"Deliver fail error: {e}", exc_info=True)
