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
from time import time

from pyrogram import Message

from .. import glovar
from ..functions.file import save

# Enable logging
logger = logging.getLogger(__name__)


def add_id(cid: int, mid: int, id_type: str) -> bool:
    # Add a id to global variables
    try:
        if not init_id(cid):
            return False

        # Add blacklist
        if id_type == "blacklist":
            if cid not in glovar.blacklist_ids:
                glovar.blacklist_ids.add(cid)
                save("blacklist_ids")

        # Add flood id
        elif id_type == "flood":
            if cid not in glovar.flood_ids["users"]:
                glovar.flood_ids["users"].add(cid)

        # Store the message's id in guest chat, in order to recall all messages sometime
        elif id_type in {"guest", "host"}:
            if mid not in glovar.message_ids[cid][id_type]:
                glovar.message_ids[cid][id_type].add(mid)
                save("message_ids")

        return True
    except Exception as e:
        logger.warning(f"Add {id_type} id error: {e}", exc_info=True)

    return False


def count_id(message: Message) -> int:
    # Count user's messages, plus one, return the total number
    try:
        if not message.from_user:
            return 0

        # Basic data
        cid = message.chat.id

        # Init ID
        if not init_id(cid):
            return 0

        # Do not count the media group message
        if message.media_group_id and message.media_group_id in glovar.media_group_ids:
            return 0

        if message.media_group_id:
            glovar.media_group_ids.add(message.media_group_id)

        # Delete old ID
        the_time = time()
        now = (message.date and message.date + the_time - int(the_time)) or the_time
        glovar.flood_ids["counts"][cid].append(now)
        for t in list(glovar.flood_ids["counts"][cid]):
            if now - t > glovar.flood_time:
                glovar.flood_ids["counts"][cid].remove(t)

        return len(glovar.flood_ids["counts"][cid])
    except Exception as e:
        logger.warning(f"Count id error: {e}", exc_info=True)

    return 0


def init_id(cid: int) -> bool:
    # Initiate the guest user's status
    try:
        if glovar.flood_ids["counts"].get(cid) is None:
            glovar.flood_ids["counts"][cid] = []

        if glovar.message_ids.get(cid) is None:
            glovar.message_ids[cid] = {
                "guest": set(),
                "host": set()
            }

        return True
    except Exception as e:
        logger.warning(f"Init id error: {e}", exc_info=True)

    return False


def remove_id(cid, mid, ctx) -> bool:
    # Remove a id in global variables
    try:
        if not init_id(cid):
            return False

        # Remove blacklisted id
        if ctx == "blacklist":
            glovar.blacklist_ids.discard(cid)
            save("blacklist_ids")

        # Remove all ids the host sent to guest chat
        elif ctx == "chat_host":
            for mid in glovar.message_ids[cid]["host"]:
                glovar.reply_ids["g2h"].pop(mid, ())
                glovar.reply_ids["h2g"].pop(mid, ())

            save("reply_ids")
            glovar.message_ids[cid]["host"] = set()
            save("message_ids")

        # Remove all ids the guest chat got
        elif ctx == "chat_all":
            for mid in glovar.message_ids[cid]["host"]:
                glovar.reply_ids["g2h"].pop(mid, ())
                glovar.reply_ids["h2g"].pop(mid, ())

            for mid in glovar.message_ids[cid]["guest"]:
                glovar.reply_ids["g2h"].pop(mid, ())
                glovar.reply_ids["h2g"].pop(mid, ())

            save("reply_ids")
            glovar.message_ids.pop(cid, {})
            save("message_ids")

        # Remove a flood user
        elif ctx == "flood":
            glovar.flood_ids["users"].discard(cid)

        # Remove a single id the host sent to guest chat
        elif ctx == "host":
            glovar.message_ids[cid]["guest"].discard(mid)
            save("message_ids")
            glovar.reply_ids["g2h"].pop(mid, ())
            glovar.reply_ids["h2g"].pop(mid, ())
            save("reply_ids")

        return True
    except Exception as e:
        logger.warning(f"Remove {ctx} id error: {e}", exc_info=True)

    return False


def reply_id(a: int, b: int, cid: int, ctx: str):
    # Add ids to "reply" records, in order to let bot know which id is corresponding to another (also know the chat id)
    try:
        if ctx == "guest":
            glovar.reply_ids["g2h"][a] = (b, cid)
        else:
            glovar.reply_ids["h2g"][a] = (b, cid)

        save("reply_ids")

        return True
    except Exception as e:
        logger.warning(f"Reply {ctx} id error: {e}", exc_info=True)

    return False
