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

from pyrogram import Client, Filters

from .. import glovar
from ..functions.etc import code, thread
from ..functions.telegram import get_user, send_message

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.private & Filters.command(command=["start"],
                                                                        prefix=glovar.prefix))
def start(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            text = ("您的传送信使已准备就绪！\n"
                    "请勿停用机器人，否则无法收到他人的消息\n"
                    "关注[此页面](https://scp-079.org/pm/)可及时获取更新信息")
        else:
            master = get_user(client, glovar.creator_id)
            text = ("欢迎使用！\n"
                    f"如您需要私聊 {code(master.first_name)}，您可以直接在此发送消息并等待回复\n"
                    "若您也想拥有自己的私聊机器人，请参照[说明](https://scp-079.org/pm/)建立")

        thread(send_message, (client, aid, text))
    except Exception as e:
        logger.warning(f"Start error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & Filters.command(command=["ping"],
                                                                        prefix=glovar.prefix))
def ping(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            text = code("Pong!")
            thread(send_message, (client, aid, text))
    except Exception as e:
        logger.warning(f"Ping error: {e}", exc_info=True)
