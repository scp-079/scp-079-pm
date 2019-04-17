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

from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup

from .. import glovar
from ..functions.etc import bytes_data, code, thread
from ..functions.ids import add_id, remove_id
from ..functions.telegram import delete_all_message, get_user, send_message

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.private & Filters.command(commands=["block"],
                                                                        prefix=glovar.prefix))
def block(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            mid = message.message_id
            if message.reply_to_message:
                rid = message.reply_to_message.from_user.id
                if rid == glovar.me_id and "ID" in message.reply_to_message.text:
                    r_message = message.reply_to_message
                    cid = int(r_message.text.partition("\n")[0].partition("ID")[2][1:])
                    if cid not in glovar.blacklist_ids:
                        add_id(cid, 0, "blacklist")
                        if glovar.message_ids[cid]["to"]:
                            thread(delete_all_message, (client, cid, glovar.message_ids[cid]["to"]))

                        if glovar.message_ids[cid]["from"]:
                            thread(delete_all_message, (client, cid, glovar.message_ids[cid]["from"]))

                        remove_id(cid, mid, "chat_all")
                        text = (f"用户 ID：[{cid}](tg://user?id={cid})\n"
                                f"状态：{code('已拉黑')}")
                    else:
                        text = (f"用户 ID：[{cid}](tg://user?id={cid})\n"
                                f"状态：{code('已在黑名单中，无需操作')}")

                    thread(send_message, (client, aid, text, mid))
                else:
                    text = "如需拉黑某人，请回复某条包含该用户 id 的汇报消息"
                    thread(send_message, (client, aid, text, mid))
            else:
                text = "如需拉黑某人，请回复某条包含该用户 id 的汇报消息"
                thread(send_message, (client, aid, text, mid))
    except Exception as e:
        logger.warning(f"Block error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & Filters.command(commands=["ping"],
                                                                        prefix=glovar.prefix))
def ping(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            text = code("Pong!")
            thread(send_message, (client, aid, text))
    except Exception as e:
        logger.warning(f"Ping error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & Filters.command(commands=["recall"],
                                                                        prefix=glovar.prefix))
def recall(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            mid = message.message_id
            if message.reply_to_message:
                rid = message.reply_to_message.from_user.id
                if rid == glovar.me_id and "ID" in message.reply_to_message.text:
                    r_message = message.reply_to_message
                    cid = int(r_message.text.partition("\n")[0].partition("ID")[2][1:])
                    text = (f"对话 ID：[{cid}](tg://user?id={cid})\n"
                            f"请选择要撤回全部消息的类别：")
                    data_to = bytes_data("recall", "to", str(cid))
                    data_all = bytes_data("recall", "all", str(cid))
                    markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "由您发送的消息",
                                    callback_data=data_to
                                ),
                                InlineKeyboardButton(
                                    "全部对话消息",
                                    callback_data=data_all
                                )
                            ]
                        ]
                    )
                    thread(send_message, (client, aid, text, mid, markup))
                else:
                    text = "如需撤回某对话的全部消息，请回复某条包含该用户 id 的汇报消息"
                    thread(send_message, (client, aid, text, mid))
            else:
                text = "如需撤回某对话的全部消息，请回复某条包含该用户 id 的汇报消息"
                thread(send_message, (client, aid, text, mid))
    except Exception as e:
        logger.warning(f"Recall error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & Filters.command(commands=["start"],
                                                                        prefix=glovar.prefix))
def start(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            text = ("您的传送信使已准备就绪！\n"
                    "请勿停用机器人，否则无法收到他人的消息\n"
                    "关注[此页面](https://scp-079.org/pm/)可及时获取更新信息")
        elif aid not in glovar.blacklist_ids and aid not in glovar.flood_ids["users"]:
            master = get_user(client, glovar.creator_id)
            text = ("欢迎使用！\n"
                    f"如您需要私聊 {code(master.first_name)}，您可以直接在此发送消息并等待回复\n"
                    "若您也想拥有自己的私聊机器人，请参照[说明](https://scp-079.org/pm/)建立")
        else:
            text = ""

        thread(send_message, (client, aid, text))
    except Exception as e:
        logger.warning(f"Start error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & Filters.command(commands=["unblock"],
                                                                        prefix=glovar.prefix))
def unblock(client, message):
    try:
        aid = message.from_user.id
        if aid == glovar.creator_id:
            mid = message.message_id
            if message.reply_to_message:
                rid = message.reply_to_message.from_user.id
                if rid == glovar.me_id and "ID" in message.reply_to_message.text:
                    r_message = message.reply_to_message
                    cid = int(r_message.text.partition("\n")[0].partition("ID")[2][1:])
                    if cid in glovar.blacklist_ids:
                        remove_id(cid, 0, "blacklist")
                        text = (f"用户 ID：[{cid}](tg://user?id={cid})\n"
                                f"状态：{code('已解禁')}")
                    else:
                        text = (f"用户 ID：[{cid}](tg://user?id={cid})\n"
                                f"状态：{code('操作失败，该用户不在黑名单中')}")

                    thread(send_message, (client, aid, text, mid))
                else:
                    text = "如需解禁某人，请回复某条包含该用户 id 的汇报消息"
                    thread(send_message, (client, aid, text, mid))
            else:
                text = "如需解禁某人，请回复某条包含该用户 id 的汇报消息"
                thread(send_message, (client, aid, text, mid))
    except Exception as e:
        logger.warning(f"Unblock error: {e}", exc_info=True)
