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

from .. import glovar

# Enable logging
logger = logging.getLogger(__name__)


def clear_counts() -> bool:
    try:
        glovar.flood_ids["counts"] = {}
        return True
    except Exception as e:
        logger.warning(f"Clear counts error: {e}", exc_info=True)

    return False


def clear_flood() -> bool:
    try:
        glovar.flood_ids["users"] = set()
        return True
    except Exception as e:
        logger.warning(f"Clear flood users error: {e}", exc_info=True)

    return False
