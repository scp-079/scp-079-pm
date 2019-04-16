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
from typing import List, Set, Union

from pyrogram import ParseMode
from pyrogram.errors import FloodWait

from .. import glovar

logger = logging.getLogger(__name__)


def send_message(client, cid: int, text: str, mid: int = None, markup=None):
    try:
        if text.strip() != "":
            result = None
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
                    return result
                except FloodWait as e:
                    sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Send message to {cid} error: {e}", exc_info=True)


def edit_message(client, cid: int, mid: int, text: str, markup=None):
    try:
        if text.strip() != "":
            result = None
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
                    return result
                except FloodWait as e:
                    sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Edit message at {cid} error: {e}", exc_info=True)


def delete_single_message(client, cid: int, mid: int):
    try:
        result = None
        while not result:
            try:
                result = client.delete_messages(cid, mid)
            except FloodWait as e:
                sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Delete single message at {cid} error: {e}", exc_info=True)


def delete_all_message(client, cid: int, mid: Union[List[int], Set[int], int]):
    try:
        result = None
        while not result:
            try:
                result = client.delete_messages(cid, mid)
            except FloodWait as e:
                sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Delete all message at {cid} error: {e}", exc_info=True)


def get_user(client, uid: int):
    result = None
    try:
        while not result:
            try:
                result = client.get_users(
                    user_ids=glovar.creator_id
                )
            except FloodWait as e:
                sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Get user {uid} error: {e}", exc_info=True)

    return result


def answer_callback(client, query_id: int, text: str):
    try:
        result = None
        while not result:
            try:
                result = client.answer_callback_query(
                    callback_query_id=query_id,
                    text=text,
                    show_alert=True
                )
                return result
            except FloodWait as e:
                sleep(e.x + 1)
    except Exception as e:
        logger.warning(f"Answer query to {query_id} error: {e}", exc_info=True)
