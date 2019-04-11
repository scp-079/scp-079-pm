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
from typing import List
from configparser import ConfigParser

# Enable logging
logger = logging.getLogger(__name__)

# Read data from config.ini
token: str = ""
me_id: int = 0
creator_id: int = 0
prefix: List[str] = []
prefix_str: str = "/!！"

try:
    config = ConfigParser()
    config.read("config.ini")

    if "custom" in config:
        token = config["custom"].get("token", token)
        me_id = int(token.partition(":")[0])
        creator_id = int(config["custom"].get("creator_id", creator_id))
        prefix = list(config["custom"].get("prefix", prefix_str))
except Exception as e:
    logger.warning(f"Read data from config.ini error: {e}")

if token == "" or me_id == 0 or creator_id == 0 or prefix == []:
    logger.critical("No proper settings")
    raise SystemExit('No proper settings')

copyright_text = ("SCP-079-PM v0.1.0, Copyright (C) 2019 SCP-079-PM <https://scp-079.org/pm/>\n"
                  "Licensed under the terms of the GNU General Public License v3 or later (GPLv3+)\n")
print(copyright_text)
