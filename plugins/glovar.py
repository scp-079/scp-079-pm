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
import pickle
from configparser import RawConfigParser
from os import mkdir
from os.path import exists
from shutil import rmtree
from typing import List, Dict, Set, Tuple, Union

# Enable logging
logger = logging.getLogger(__name__)

# Init

all_commands: List[str] = [
    "block",
    "clear",
    "direct",
    "leave",
    "now",
    "ping",
    "recall",
    "start",
    "unblock",
    "version"
]

sender: str = "PM"

should_hide: bool = False

version: str = "0.4.0"

direct_chat: int = 0

# Read data from config.ini

# [basic]
bot_token: str = ""
prefix: List[str] = []
prefix_str: str = "/!"

# [channels]
exchange_channel_id: int = 0
hide_channel_id: int = 0
test_group_id: int = 0

# [custom]
host_id: int = 0
host_name: str = ""
reset_day: str = ""

try:
    config = RawConfigParser()
    config.read("config.ini")
    # [basic]
    bot_token = config["basic"].get("bot_token", bot_token)
    prefix = list(config["basic"].get("prefix", prefix_str))
    # [channels]
    exchange_channel_id = int(config["channels"].get("exchange_channel_id", exchange_channel_id))
    hide_channel_id = int(config["channels"].get("hide_channel_id", hide_channel_id))
    test_group_id = int(config["channels"].get("test_group_id", test_group_id))
    # [custom]
    host_id = int(config["custom"].get("host_id", host_id))
    host_name = config["custom"].get("host_name", host_name)
    reset_day = config["custom"].get("reset_day", reset_day)
except Exception as e:
    logger.warning(f"Read data from config.ini error: {e}")

# Check
if (bot_token in {"", "[DATA EXPUNGED]"}
        or prefix == []
        or host_id == 0
        or host_name in {"", "[DATA EXPUNGED]"}
        or reset_day in {"", "[DATA EXPUNGED]"}):
    raise SystemExit('No proper settings')

# Load data from pickle

# Init dir
try:
    rmtree("tmp")
except Exception as e:
    logger.info(f"Remove tmp error: {e}")

for path in ["data", "tmp"]:
    if not exists(path):
        mkdir(path)

# Init ids variables

blacklist_ids: Set[int] = set()
# blacklist_ids = {12345678}

flood_ids: Dict[str, Union[Dict[int, int], set]] = {
    "users": set(),
    "counts": {}
}
# flood_ids = {
#     "users": {12345678},
#     "counts": {12345678: 0}
# }

message_ids: Dict[int, Dict[str, Set[int]]] = {}
# message_ids = {
#     12345678: {
#         "guest": {123},
#         "host": {456}
#     }
# }

reply_ids: Dict[str, Dict[int, Tuple[int, int]]] = {
    "g2h": {},
    "h2g": {}
}
# reply_ids = {
#     "g2h": {
#         123: (124, 12345678)
#     },
#     "h2g": {
#         124: (123, 12345678)
#     }
# }

# Load ids data
file_list: List[str] = ["blacklist_ids", "message_ids", "reply_ids"]
for file in file_list:
    try:
        try:
            if exists(f"data/{file}") or exists(f"data/.{file}"):
                with open(f"data/{file}", 'rb') as f:
                    locals()[f"{file}"] = pickle.load(f)
            else:
                with open(f"data/{file}", 'wb') as f:
                    pickle.dump(eval(f"{file}"), f)
        except Exception as e:
            logger.error(f"Load data {file} error: {e}")
            with open(f"data/.{file}", 'rb') as f:
                locals()[f"{file}"] = pickle.load(f)
    except Exception as e:
        logger.critical(f"Load data {file} backup error: {e}")
        raise SystemExit("[DATA CORRUPTION]")

# Start program
copyright_text = (f"SCP-079-{sender} v{version}, Copyright (C) 2019 SCP-079 <https://scp-079.org>\n"
                  "Licensed under the terms of the GNU General Public License v3 or later (GPLv3+)\n")
print(copyright_text)
