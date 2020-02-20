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
from time import sleep

from pyrogram import Client

from .. import glovar
from .channel import share_data
from .etc import code, general_link, get_now, lang, thread
from .file import save
from .telegram import send_message

# Enable logging
logger = logging.getLogger(__name__)


def backup_files(client: Client) -> bool:
    # Backup data files to BACKUP
    try:
        for file in glovar.file_list:
            # Check
            if not eval(f"glovar.{file}"):
                continue

            # Share
            share_data(
                client=client,
                receivers=["BACKUP"],
                action="backup",
                action_type="data",
                data=file,
                file=f"data/{file}"
            )
            sleep(5)

        return True
    except Exception as e:
        logger.warning(f"Backup error: {e}", exc_info=True)

    return False


def interval_min_01() -> bool:
    # Execute very minute
    glovar.locks["guest"].acquire()
    try:
        # Basic data
        now = get_now()

        # Clear the user's flood status
        for uid in list(glovar.flood_ids["users"]):
            if now - glovar.flood_ids["users"][uid] > glovar.flood_ban:
                glovar.flood_ids["users"].pop(uid, 0)

        return True
    except Exception as e:
        logger.warning(f"Interval min 01 error: {e}", exc_info=True)
    finally:
        glovar.locks["guest"].release()

    return False


def reset_data(client: Client) -> bool:
    # Reset user data every month
    try:
        glovar.bad_ids = {
            "users": set()
        }
        save("bad_ids")

        glovar.message_ids = {}
        save("message_ids")

        glovar.reply_ids = {
            "g2h": {},
            "h2g": {}
        }
        save("reply_ids")

        # Send debug message
        text = (f"{lang('project')}{lang('colon')}{general_link(glovar.project_name, glovar.project_link)}\n"
                f"{lang('action')}{lang('colon')}{code(lang('reset'))}\n")
        glovar.debug_channel_id and thread(send_message, (client, glovar.debug_channel_id, text))

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


def update_status(client: Client, the_type: str) -> bool:
    # Update running status to BACKUP
    try:
        share_data(
            client=client,
            receivers=["BACKUP"],
            action="backup",
            action_type="status",
            data={
                "type": the_type,
                "backup": glovar.backup
            }
        )

        return True
    except Exception as e:
        logger.warning(f"Update status error: {e}", exc_info=True)

    return False
