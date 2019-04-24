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
from typing import Iterable, List, Optional

from pyrogram import Client, InlineKeyboardMarkup, Message, ParseMode, User
from pyrogram.errors import FloodWait

logger = logging.getLogger(__name__)


def answer_callback(client: Client, query_id: str, text: str) -> Optional[bool]:
    result = None
    try:
        while not result:
            try:
                result = client.answer_callback_query(
                    callback_query_id=query_id,
                    text=text,
                    show_alert=True
                )
            except FloodWait as e:
                sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Answer query to {query_id} error: {e}", exc_info=True)

    return result


def edit_message_text(client: Client, cid: int, mid: int, text: str,
                      markup: InlineKeyboardMarkup = None) -> Optional[Message]:
    result = None
    try:
        if text.strip() != "":
            while not result:
                try:
                    result = client.edit_message_text(
                        chat_id=cid,
                        message_id=mid,
                        text=text,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                        reply_markup=markup
                    )
                except FloodWait as e:
                    sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Edit message in {cid} error: {e}", exc_info=True)

    return result


def delete_messages(client: Client, cid: int, mids: Iterable[int]) -> Optional[bool]:
    result = None
    try:
        while not result:
            try:
                result = client.delete_messages(cid, mids)
            except FloodWait as e:
                sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Delete messages in {cid} error: {e}", exc_info=True)

    return result


def get_users(client: Client, uids: Iterable[int]) -> Optional[List[User]]:
    result = None
    try:
        while not result:
            try:
                result = client.get_users(user_ids=uids)
            except FloodWait as e:
                sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Get users {uids} error: {e}", exc_info=True)

    return result


def send_message(client: Client, cid: int, text: str, mid: int = None,
                 markup: InlineKeyboardMarkup = None) -> Optional[Message]:
    result = None
    try:
        if text.strip() != "":
            while not result:
                try:
                    result = client.send_message(
                        chat_id=cid,
                        text=text,
                        parse_mode=ParseMode.MARKDOWN,
                        disable_web_page_preview=True,
                        reply_to_message_id=mid,
                        reply_markup=markup
                    )
                except FloodWait as e:
                    sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Send message to {cid} error: {e}", exc_info=True)

    return result
