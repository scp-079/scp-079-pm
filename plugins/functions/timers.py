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

from pyrogram import Client

from .. import glovar
from .channel import share_data
from .file import save

# Enable logging
logger = logging.getLogger(__name__)


def interval_sec_05() -> bool:
    # Execute very 5 seconds
    try:
        # Clear the user's flood counts
        for uid in list(glovar.flood_ids["counts"]):
            glovar.flood_ids["counts"][uid] = 0

        return True
    except Exception as e:
        logger.warning(f"Interval sec 05 error: {e}", exc_info=True)

    return False


def interval_min_15() -> bool:
    # Execute very 15 minutes
    try:
        # Clear the user's flood status
        glovar.flood_ids["users"] = set()

        return True
    except Exception as e:
        logger.warning(f"Interval min 15 error: {e}", exc_info=True)

    return False


def reset_data() -> bool:
    # Reset user data every month
    try:
        glovar.message_ids = {}
        save("message_ids")

        glovar.reply_ids = {
            "g2h": {},
            "h2g": {}
        }
        save("reply_ids")

        return True
    except Exception as e:
        logger.warning(f"Reset data error: {e}", exc_info=True)

    return False


def reset_direct() -> bool:
    # Reset direct chat every day
    try:
        glovar.direct_chat = 0

        return True
    except Exception as e:
        logger.warning(f"Reset direct error: {e}", exc_info=True)

    return False


def update_status(client: Client) -> bool:
    # Update running status to BACKUP
    try:
        share_data(
            client=client,
            receivers=["BACKUP"],
            action="backup",
            action_type="status",
            data="awake"
        )

        return True
    except Exception as e:
        logger.warning(f"Update status error: {e}")

    return False
