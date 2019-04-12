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
from threading import Thread
from typing import Callable

# Enable logging
logger = logging.getLogger(__name__)


def code(text) -> str:
    if text != "":
        return f"`{text}`"

    return ""


def code_block(text) -> str:
    if text != "":
        return f"```{text}````"

    return ""


def thread(target: Callable, args: tuple):
    t = Thread(target=target, args=args)
    t.daemon = True
    t.start()


def bytes_data(action: str, call_type: str, data) -> bytes:
    text = ('{'
            f'"action":"{action}",'
            f'"type":"{call_type}",'
            f'"data":"{data}"'
            '}')

    return text.encode("utf-8")
