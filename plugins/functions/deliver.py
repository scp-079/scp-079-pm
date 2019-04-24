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

from pyrogram import Client, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import FloodWait, UserIsBlocked

from .. import glovar
from .etc import button_data, code, thread, user_mention
from .ids import add_id, reply_id
from .telegram import send_message

# Enable logging
logger = logging.getLogger(__name__)


def deliver_guest_message(client: Client, message: Message) -> bool:
    try:
        hid = glovar.host_id
        cid = message.chat.id
        mid = message.message_id
        mids = [mid]
        if message.forward_from or message.forward_from_chat or message.forward_from_name:
            as_copy = False
        else:
            as_copy = True

        result = None
        while not result:
            try:
                result = client.forward_messages(
                    chat_id=hid,
                    from_chat_id=cid,
                    message_ids=mids,
                    disable_notification=True,
                    as_copy=as_copy
                )
            except FloodWait as e:
                sleep(e.x + 1)
            except UserIsBlocked:
                deliver_fail(client, cid, mid)
                return False
            except Exception as e:
                logger.warning(f"Forward message error: {e}")
                return False

        text = (f"用户 ID：{code(cid)}\n"
                f"昵称：[{message.from_user.first_name}](tg://user?id={cid})")
        forward_mid = result.message_id
        thread(send_message, (client, hid, text, forward_mid))
        add_id(cid, mid, "guest")
        reply_id(mid, forward_mid, cid, "guest")
        return True
    except Exception as e:
        logger.warning(f"Deliver guest message error: {e}", exc_info=True)

    return False


def deliver_host_message(client: Client, message: Message) -> bool:
    try:
        r_message = message.reply_to_message
        cid = int(r_message.text.partition("\n")[0].partition("ID")[2][1:])
        hid = glovar.host_id
        mid = message.message_id
        mids = [mid]
        if cid not in glovar.blacklist_ids:
            if message.forward_from or message.forward_from_chat or message.forward_from_name:
                as_copy = False
            else:
                as_copy = True

            result = None
            while not result:
                try:
                    result = client.forward_messages(
                        chat_id=cid,
                        from_chat_id=hid,
                        message_ids=mids,
                        disable_notification=True,
                        as_copy=as_copy
                    )
                except FloodWait as e:
                    sleep(e.x + 1)
                except UserIsBlocked:
                    deliver_fail(client, hid, mid)
                    return False
                except Exception as e:
                    logger.warning(f"Forward message error: {e}")
                    return False

            text = (f"发送至 ID：[{cid}](tg://user?id={cid})\n"
                    f"状态：{code('已发送')}")
            forward_mid = result.message_id
            data = button_data("recall", "single", str(forward_mid))
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
            thread(send_message, (client, hid, text, mid, markup))
            add_id(cid, forward_mid, "host")
            reply_id(mid, forward_mid, cid, "host")
        else:
            text = (f"发送至 ID：{user_mention(cid)}\n"
                    f"状态：{code('发送失败')}\n"
                    f"原因：{code('该用户在黑名单中')}")
            thread(send_message, (client, hid, text, mid))

        return False
    except Exception as e:
        logger.warning(f"Deliver host message error: {e}", exc_info=True)

    return False


def deliver_fail(client: Client, cid: int, mid: int) -> bool:
    try:
        text = (f"状态：{code('发送失败')}\n"
                f"原因：{code('对方已停用机器人')}")
        thread(send_message, (client, cid, text, mid))
        return True
    except Exception as e:
        logger.warning(f"Deliver fail error: {e}", exc_info=True)

    return False
