# SCP-079-PM - Everyone can have their own Telegram private chat bot
# Copyright (C) 2019-2020 SCP-079 <https://scp-079.org>
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
from html import escape
from json import dumps, loads
from random import choice, uniform
from string import ascii_letters, digits
from threading import Thread
from time import sleep, time
from typing import Any, Callable, List, Optional, Union

from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup, Message, User
from pyrogram.errors import FloodWait

from .. import glovar

# Enable logging
logger = logging.getLogger(__name__)


def bold(text: Any) -> str:
    # Get a bold text
    try:
        text = str(text).strip()
        if text:
            return f"<b>{escape(text)}</b>"
    except Exception as e:
        logger.warning(f"Bold error: {e}", exc_info=True)

    return ""


def button_data(action: str, action_type: str = None, data: Union[int, str] = None) -> Optional[bytes]:
    # Get a button's bytes data
    result = None
    try:
        button = {
            "a": action,
            "t": action_type,
            "d": data
        }
        result = dumps(button).replace(" ", "").encode("utf-8")
    except Exception as e:
        logger.warning(f"Button data error: {e}", exc_info=True)

    return result


def code(text: Any) -> str:
    # Get a code text
    try:
        text = str(text).strip()
        if text:
            return f"<code>{escape(text)}</code>"
    except Exception as e:
        logger.warning(f"Code error: {e}", exc_info=True)

    return ""


def code_block(text: Any) -> str:
    # Get a code block text
    try:
        text = str(text).rstrip()
        if text:
            return f"<pre>{escape(text)}</pre>"
    except Exception as e:
        logger.warning(f"Code block error: {e}", exc_info=True)

    return ""


def general_link(text: Union[int, str], link: str) -> str:
    # Get a general link
    result = ""
    try:
        text = str(text).strip()
        link = link.strip()
        if text and link:
            result = f'<a href="{link}">{escape(text)}</a>'
    except Exception as e:
        logger.warning(f"General link error: {e}", exc_info=True)

    return result


def get_callback_data(message: Message) -> List[dict]:
    # Get a message's inline button's callback data
    callback_data_list = []
    try:
        reply_markup = message.reply_markup

        if (not reply_markup
                or not isinstance(reply_markup, InlineKeyboardMarkup)
                or not reply_markup.inline_keyboard):
            return []

        for button_row in reply_markup.inline_keyboard:
            for button in button_row:
                if not button.callback_data:
                    continue

                callback_data = button.callback_data
                callback_data = loads(callback_data)
                callback_data_list.append(callback_data)
    except Exception as e:
        logger.warning(f"Get callback data error: {e}", exc_info=True)

    return callback_data_list


def get_command_type(message: Message) -> str:
    # Get the command type "a" in "/command a"
    result = ""
    try:
        text = get_text(message)
        command_list = list(filter(None, text.split(" ")))
        result = text[len(command_list[0]):].strip()
    except Exception as e:
        logger.warning(f"Get command type error: {e}", exc_info=True)

    return result


def get_full_name(user: User) -> str:
    # Get user's full name
    text = ""
    try:
        if not user or user.is_deleted:
            return ""

        text = user.first_name
        if user.last_name:
            text += f" {user.last_name}"
    except Exception as e:
        logger.warning(f"Get full name error: {e}", exc_info=True)

    return text


def get_int(text: str) -> Optional[int]:
    # Get a int from a string
    result = None
    try:
        result = int(text)
    except Exception as e:
        logger.info(f"Get int error: {e}", exc_info=True)

    return result


def get_list_page(the_list: list, action: str, action_type: str, page: int) -> (list, InlineKeyboardMarkup):
    # Generate a list for elements and markup buttons
    markup = None
    try:
        per_page = glovar.per_page
        quo = int(len(the_list) / per_page)

        if quo == 0:
            return the_list, None

        page_count = quo + 1

        if len(the_list) % per_page == 0:
            page_count = page_count - 1

        if page != page_count:
            the_list = the_list[(page - 1) * per_page:page * per_page]
        else:
            the_list = the_list[(page - 1) * per_page:len(the_list)]

        if page_count == 1:
            return the_list, markup

        if page == 1:
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=lang("page").format(page),
                            callback_data=button_data("none")
                        ),
                        InlineKeyboardButton(
                            text=">>",
                            callback_data=button_data(action, action_type, page + 1)
                        )
                    ]
                ]
            )
        elif page == page_count:
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="<<",
                            callback_data=button_data(action, action_type, page - 1)
                        ),
                        InlineKeyboardButton(
                            text=lang("page").format(page),
                            callback_data=button_data("none")
                        )
                    ]
                ]
            )
        else:
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="<<",
                            callback_data=button_data(action, action_type, page - 1)
                        ),
                        InlineKeyboardButton(
                            text=lang("page").format(page),
                            callback_data=button_data("none")
                        ),
                        InlineKeyboardButton(
                            text=">>",
                            callback_data=button_data(action, action_type, page + 1)
                        )
                    ]
                ]
            )
    except Exception as e:
        logger.warning(f"Get list page error: {e}", exc_info=True)

    return the_list, markup


def get_now() -> int:
    # Get time for now
    result = 0
    try:
        result = int(time())
    except Exception as e:
        logger.warning(f"Get now error: {e}", exc_info=True)

    return result


def get_text(message: Message) -> str:
    # Get message's text
    text = ""
    try:
        if not message:
            return ""

        the_text = message.text or message.caption
        if the_text:
            text += the_text
    except Exception as e:
        logger.warning(f"Get text error: {e}", exc_info=True)

    return text


def lang(text: str) -> str:
    # Get the text
    result = ""
    try:
        result = glovar.lang.get(text, text)
    except Exception as e:
        logger.warning(f"Lang error: {e}", exc_info=True)

    return result


def mention_id(uid: int) -> str:
    # Get a ID mention string
    result = ""
    try:
        result = general_link(f"{uid}", f"tg://user?id={uid}")
    except Exception as e:
        logger.warning(f"Mention id error: {e}", exc_info=True)

    return result


def mention_name(user: User) -> str:
    # Get a name mention string
    result = ""
    try:
        name = get_full_name(user)
        uid = user.id
        result = general_link(f"{name}", f"tg://user?id={uid}")
    except Exception as e:
        logger.warning(f"Mention name error: {e}", exc_info=True)

    return result


def random_str(i: int) -> str:
    # Get a random string
    text = ""
    try:
        text = "".join(choice(ascii_letters + digits) for _ in range(i))
    except Exception as e:
        logger.warning(f"Random str error: {e}", exc_info=True)

    return text


def thread(target: Callable, args: tuple) -> bool:
    # Call a function using thread
    try:
        t = Thread(target=target, args=args)
        t.daemon = True
        t.start()

        return True
    except Exception as e:
        logger.warning(f"Thread error: {e}", exc_info=True)

    return False


def wait_flood(e: FloodWait) -> bool:
    # Wait flood secs
    try:
        sleep(e.x + uniform(0.5, 1.0))

        return True
    except Exception as e:
        logger.warning(f"Wait flood error: {e}", exc_info=True)

    return False
