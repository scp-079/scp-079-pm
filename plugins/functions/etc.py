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
from json import dumps, loads
from threading import Thread
from typing import Callable, List, Union

from pyrogram import InlineKeyboardMarkup, Message, User

# Enable logging
logger = logging.getLogger(__name__)


def bold(text) -> str:
    # Get a bold text
    if text:
        return f"**{text}**"

    return ""


def button_data(action: str, action_type: str = None, data: Union[int, str] = None) -> bytes:
    # Get a button's bytes data
    button = {
        "a": action,
        "t": action_type,
        "d": data
    }
    return dumps(button).replace(" ", "").encode("utf-8")


def code(text) -> str:
    # Get a code text
    if text:
        return f"`{text}`"

    return ""


def code_block(text) -> str:
    # Get a code block text
    if text:
        return f"```{text}```"

    return ""


def format_data(sender: str, receivers: List[str], action: str, action_type: str, data=None) -> str:
    # See https://scp-079.org/exchange/
    data = {
        "from": sender,
        "to": receivers,
        "action": action,
        "type": action_type,
        "data": data
    }

    return code_block(dumps(data, indent=4))


def general_link(text: Union[int, str], link: str) -> str:
    # Get a general markdown link
    return f"[{text}]({link})"


def get_callback_data(message: Message) -> List[dict]:
    # Get a message's inline button's callback data
    callback_data_list = []
    try:
        logger.warning(message)
        if message.reply_markup and isinstance(message.reply_markup, InlineKeyboardMarkup):
            reply_markup = message.reply_markup
            if reply_markup.inline_keyboard:
                inline_keyboard = reply_markup.inline_keyboard
                if inline_keyboard:
                    for button in inline_keyboard:
                        if button.callback_data:
                            callback_data = button.callback_data
                            callback_data = loads(callback_data)
                            callback_data_list.append(callback_data)
    except Exception as e:
        logger.warning(f"Get callback data error: {e}", exc_info=True)

    return callback_data_list


def get_text(message: Message) -> str:
    # Get message's text
    text = ""
    try:
        if message.text or message.caption:
            if message.text:
                text += message.text
            else:
                text += message.caption
    except Exception as e:
        logger.warning(f"Get text error: {e}", exc_info=True)

    return text


def name_mention(user: User) -> str:
    # Get a mention text with user's name
    name = user.first_name
    uid = user.id

    return f"[{name}](tg://user?id={uid})"


def thread(target: Callable, args: tuple) -> bool:
    # Call a function using thread
    t = Thread(target=target, args=args)
    t.daemon = True
    t.start()

    return True


def user_mention(uid: int) -> str:
    # Get a mention text
    return f"[{uid}](tg://user?id={uid})"
