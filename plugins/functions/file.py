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
from pickle import dump
from shutil import copyfile
from threading import Thread

from .. import glovar

# Enable logging
logger = logging.getLogger(__name__)


def save(file: str) -> bool:
    # Save a global variable to a file
    t = Thread(target=save_thread, args=(file,))
    t.start()

    return True


def save_thread(file: str) -> bool:
    try:
        if glovar:
            with open(f"data/.{file}", "wb") as f:
                dump(eval(f"glovar.{file}"), f)

            copyfile(f"data/.{file}", f"data/{file}")

        return True
    except Exception as e:
        logger.error(f"Save data error: {e}", exc_info=True)

    return False
