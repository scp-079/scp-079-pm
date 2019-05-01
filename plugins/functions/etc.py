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
from json import dumps
from threading import Thread
from typing import Callable, List, Union

from pyrogram import User

# Enable logging
logger = logging.getLogger(__name__)


def bold(text) -> str:
    if text != "":
        return f"**{text}**"

    return ""


def button_data(action: str, action_type: str = None, data: Union[int, str] = None) -> bytes:
    button = {
        "a": action,
        "t": action_type,
        "d": data
    }
    return dumps(button).replace(" ", "").encode("utf-8")


def code(text) -> str:
    if text != "":
        return f"`{text}`"

    return ""


def code_block(text) -> str:
    if text != "":
        return f"```{text}```"

    return ""


def format_data(sender: str, receivers: List[str], action: str, action_type: str, data=None) -> str:
    """Make a unified format string for data exchange.

    Args:
        sender (str):
            The sender's name.

        receivers (list of str):
            The receivers' names.

        action (str):
            The action that the data receivers need to take. It can be any of the followings:
                add - Add id to some list
                backup - Send backup data
                config - Update bot config
                declare - Declare a message
                help - Let others bot do something
                join - Let bots join some group
                leave - Let bots leave some group
                remove - Remove id in some list
                update - Update some data

        action_type (str):
            Type of action. It can be any of the followings:
                When action is add or remove:
                    bad - Spam channel or user
                    except - Exception channel or user
                    watch - Suspicious user.
                            Recommended to ban user or delete user's messages when meets certain conditions

                When action is backup:
                    pickle - Pickle file

                When action is config:
                    ask - Let CONFIG provide config options in CONFIG Channel
                    commit - Update group's configurations
                    reply - CONFIG reply the config link to bot

                When action is declare:
                    ban - The bot has banned the user who sent the message
                    delete - The message has been deleted

                When action is help:
                    ban - Let USER ban a user globally
                    delete - Let USER delete a user's all messages in some group
                    report - Let WARN alert admins

                When action is join:
                    approve - Let USER invite bots to a group
                    request - Send a join request to MANAGE
                    status - Send USER permission status to MANAGE
                    update - Let USER update the permission status

                When action is leave:
                    approve - Let bot leave a group
                    info - Send auto left group info to MANAGE
                    request - Send a leave request to MANAGE

                When action is update:
                    download - Download the data, then update
                    preview - Update a message's preview
                    reload - Update the data from local machines
                    score - Update user's score
                    status - Update bot's status


        data (optional):
            Additional data required for operation.
                Add / Remove:
                    bad / except
                        {
                            "id":  12345678,
                            "type": "user / channel"
                        }

                    watch:
                        {
                            "id": 12345678,
                            "type": "all / ban / delete"
                        }

                Backup:
                    "filename"

                Config:
                    ask:
                        {
                            "project_name": "Project name",
                            "project_link": "Link to project",
                            "group_id": -10012345678,
                            "group_name": "Group Name",
                            "group_link": "link to group",
                            "user_id": 12345678
                            "config": dict,
                            "default": dict
                        }

                    commit:
                        {
                            "group_id": -10012345678,
                            "config": dict
                        }

                    reply:
                        {
                            "group_id": -10012345678,
                            "user_id": 12345678,
                            "config_link": "link to config"
                        }

                Declare:
                    {
                        "group_id": -10012345678,
                        "message_id": 123
                    }

                Help:
                    ban / delete:
                        {
                            "group_id": -10012345678,
                            "user_id": 12345678
                        }

                    report:
                        {
                            "group_id": -10012345678,
                            "user_id": 12345678,
                            "message_id": 123
                        }

                Join:
                    approve:
                        {
                            "id": "random",
                            "bots": List[str]
                        }

                    request:
                        {
                            "id": "random",
                            "bots": List[str],
                            "group_link": "link to group",
                            "user_id": 12345678
                        }

                    status:
                        {
                            "id": "random",
                            "status": "left / permission / invalid" / -10012345678
                        }

                    update:
                        "random id"

                Leave:
                    approve:
                        {
                            "group_id": -10012345678,
                            "reason": "reason here"
                        }

                    info:
                        -10012345678

                    request:
                        {
                            "group_id": -10012345678,
                            "group_name": "Group Name",
                            "group_link": "link to group",
                            "reason": "user / permissions"
                        }

                Score:
                    3.2

                Update
                    download:
                        "filename"

                    preview: {
                        "group_id": -10012345678,
                        "user_id": 12345678,
                        "message_id": 123,
                        "text": "some text",
                        "image": "file_id"
                    }

                    reload:
                        "path"

                    score:
                        {
                            "id": 12345678,
                            "score": 3.2
                        }

                    status:
                        "awake"

    Returns:
        A formatted string.
    """
    data = {
        "from": sender,
        "to": receivers,
        "action": action,
        "type": action_type,
        "data": data
    }

    return code_block(dumps(data, indent=4))


def general_link(text: Union[int, str], link: str) -> str:
    return f"[{text}]({link})"


def name_mention(user: User) -> str:
    name = user.first_name
    uid = user.id

    return f"[{name}](tg://user?id={uid})"


def thread(target: Callable, args: tuple) -> bool:
    t = Thread(target=target, args=args)
    t.daemon = True
    t.start()

    return True


def user_mention(uid: int) -> str:
    return f"[{uid}](tg://user?id={uid})"
