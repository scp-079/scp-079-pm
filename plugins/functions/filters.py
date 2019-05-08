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

from typing import Union

from pyrogram import CallbackQuery, Filters, Message

from .. import glovar


def is_host_chat(_, update: Union[CallbackQuery, Message]) -> bool:
    # Check if the update is in the host chat
    if isinstance(update, CallbackQuery):
        message = update.message
    else:
        message = update

    cid = message.chat.id
    if cid == glovar.host_id:
        return True

    return False


def is_limited_user(_, message: Message) -> bool:
    # Check if the message is sent by a limited user
    cid = message.chat.id
    if cid in glovar.blacklist_ids or cid in glovar.flood_ids["users"]:
        return True

    return False


def is_test_group(_, message: Message) -> bool:
    # Check if the message is sent from test group
    cid = message.chat.id
    if cid == glovar.test_group_id:
        return True

    return False


host_chat = Filters.create(
    name="Host Chat",
    func=is_host_chat
)

limited_user = Filters.create(
    name="Limited User",
    func=is_limited_user
)

test_group = Filters.create(
    name="Test Group",
    func=is_test_group
)
