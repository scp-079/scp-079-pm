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
from .. functions.deliver import clear_data, get_guest, recall_messages
from ..functions.etc import bold, button_data, code, code_block, general_link, get_callback_data, get_text
from ..functions.etc import thread, user_mention
from ..functions.filters import host_chat, test_group
from ..functions.ids import add_id, remove_id
from ..functions.telegram import delete_messages, edit_message_reply_markup, get_users, send_message

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.private & host_chat
                   & Filters.command(["block"], glovar.prefix))
def block(client, message):
    try:
        hid = message.from_user.id
        mid = message.message_id
        _, cid = get_guest(message)
        if cid:
            if cid not in glovar.blacklist_ids:
                add_id(cid, 0, "blacklist")
                # When add someone to blacklist, delete all messages in this guest's chat
                if glovar.message_ids[cid]["host"]:
                    thread(delete_messages, (client, cid, [glovar.message_ids[cid]["host"]]))

                if glovar.message_ids[cid]["guest"]:
                    thread(delete_messages, (client, cid, [glovar.message_ids[cid]["guest"]]))

                remove_id(cid, mid, "chat_all")
                text = (f"用户 ID：{user_mention(cid)}\n"
                        f"状态：{code('已拉黑')}\n")
            else:
                text = (f"用户 ID：{user_mention(cid)}\n"
                        f"状态：{code('无需操作')}\n"
                        f"原因：{code('该用户已在黑名单中')}\n")

            thread(send_message, (client, hid, text, mid))
        else:
            text = "如需拉黑某人，请回复某条包含该用户 ID 的汇报消息\n"
            thread(send_message, (client, hid, text, mid))
    except Exception as e:
        logger.warning(f"Block error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & host_chat
                   & Filters.command(["clear"], glovar.prefix))
def clear(client, message):
    try:
        hid = message.from_user.id
        mid = message.message_id
        message_text = get_text(message)
        command_list = list(filter(None, message_text.split(" ")))
        if len(command_list) == 1:
            text = "请选择要清空的数据\n"
            data_reply = button_data("clear", "messages", 0)
            data_blacklist = button_data("clear", "blacklist", 0)
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "消息 ID",
                            callback_data=data_reply
                        ),
                        InlineKeyboardButton(
                            "黑名单",
                            callback_data=data_blacklist
                        )
                    ]
                ]
            )
        elif len(command_list) == 2 and command_list[1] in {"blacklist", "messages"}:
            text = clear_data(command_list[1])
            markup = None
        else:
            text = f"未操作：{code('格式有误')}"
            markup = None

        thread(send_message, (client, hid, text, mid, markup))
    except Exception as e:
        logger.warning(f"Clear error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & host_chat
                   & Filters.command(["direct"], glovar.prefix))
def direct_chat(client, message):
    try:
        hid = message.from_user.id
        mid = message.message_id
        _, cid = get_guest(message)
        if cid:
            if cid not in glovar.blacklist_ids:
                glovar.direct_chat = cid
                text = (f"用户 ID：{user_mention(cid)}\n"
                        f"状态：{code('已开始与该用户的直接对话')}\n")
            else:
                text = (f"用户 ID：{user_mention(cid)}\n"
                        f"状态：{code('操作失败')}\n"
                        f"原因：{code('该用户在黑名单中')}\n")

            thread(send_message, (client, hid, text, mid))
        else:
            text = "如需与某人直接对话，请回复某条包含该用户 ID 的汇报消息\n"
            thread(send_message, (client, hid, text, mid))
    except Exception as e:
        logger.warning(f"Direct chat error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & host_chat
                   & Filters.command(["leave"], glovar.prefix))
def leave_chat(client, message):
    try:
        hid = message.from_user.id
        cid = glovar.direct_chat
        if cid:
            glovar.direct_chat = 0
            text = (f"用户 ID：{user_mention(cid)}\n"
                    f"状态：{code('已退出与该用户的直接对话')}\n")
        else:
            text = (f"状态：{code('操作失败')}\n"
                    f"原因：{code('当前无直接对话')}\n")

        thread(send_message, (client, hid, text))
    except Exception as e:
        logger.warning(f"Leave chat error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & host_chat
                   & Filters.command(["now"], glovar.prefix))
def now_chat(client, message):
    try:
        hid = message.from_user.id
        cid = glovar.direct_chat
        if cid:
            text = (f"用户 ID：{user_mention(cid)}\n"
                    f"状态：{code('正在与该用户直接对话')}\n")
        else:
            text = f"状态：{code('当前无直接对话')}\n"

        thread(send_message, (client, hid, text))
    except Exception as e:
        logger.warning(f"Now chat error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & host_chat
                   & Filters.command(["ping"], glovar.prefix))
def ping(client, message):
    try:
        hid = message.from_user.id
        text = code("Pong!")
        thread(send_message, (client, hid, text))
    except Exception as e:
        logger.warning(f"Ping error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & host_chat
                   & Filters.command(["recall"], glovar.prefix))
def recall(client, message):
    try:
        hid = message.from_user.id
        mid = message.message_id
        recall_mid, cid = get_guest(message)
        if cid:
            message_text = get_text(message)
            command_list = list(filter(None, message_text.split(" ")))
            text = f"对话 ID：[{cid}](tg://user?id={cid})\n"
            if len(command_list) == 1:
                text += f"请选择要撤回全部消息的类别：\n"
                data_host = button_data("recall", "host", str(cid))
                data_all = button_data("recall", "all", str(cid))
                markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "由您发送的消息",
                                callback_data=data_host
                            ),
                            InlineKeyboardButton(
                                "全部对话消息",
                                callback_data=data_all
                            )
                        ]
                    ]
                )
            elif len(command_list) == 2 and command_list[1] in {"all", "host", "single"}:
                # If the host want to recall single message, bot should found which message to recall
                if command_list[1] == "single" and not recall_mid:
                    # Get the message's id from message's inline button's data
                    callback_data_list = get_callback_data(message.reply_to_message)
                    if (callback_data_list
                            and callback_data_list[0]["a"] == "recall"
                            and callback_data_list[0]["t"] == "single"):
                        recall_mid = callback_data_list[0]["d"]
                        # Edit the origin report message, delete the reply markup
                        thread(edit_message_reply_markup, (client, hid, message.reply_to_message.message_id, None))
                    # If the data cannot be found, send a error message
                    else:
                        text += (f"状态：{code('未撤回')}\n"
                                 f"原因：{code('回复有误')}\n")
                        markup = None
                        thread(send_message, (client, hid, text, mid, markup))
                        return

                text = recall_messages(client, cid, command_list[1], recall_mid)
                markup = None
            else:
                text += (f"状态：{code('未撤回')}\n"
                         f"原因：{code('格式有误')}\n")
                markup = None

            thread(send_message, (client, hid, text, mid, markup))
        else:
            text = "如需撤回某对话的全部消息，请回复某条包含该用户 ID 的汇报消息\n"
            thread(send_message, (client, hid, text, mid))
    except Exception as e:
        logger.warning(f"Recall error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private
                   & Filters.command(["start"], glovar.prefix))
def start(client, message):
    try:
        uid = message.from_user.id
        if uid == glovar.host_id:
            text = (f"您的传送信使已准备就绪\n"
                    f"请勿停用机器人，否则无法收到他人的消息\n"
                    f"关注{general_link('此页面', 'https://scp-079.org/pm/')}可及时获取更新信息\n")
        elif uid not in glovar.blacklist_ids and uid not in glovar.flood_ids["users"]:
            host = get_users(client, [glovar.host_id])[0]
            text = (f"欢迎使用\n"
                    f"如您需要私聊 {code(host.first_name)}，您可以直接在此发送消息并等待回复\n"
                    f"若您也想拥有自己的私聊机器人，请参照{general_link('说明', 'https://scp-079.org/pm/')}建立\n")
        else:
            text = ""

        thread(send_message, (client, uid, text))
    except Exception as e:
        logger.warning(f"Start error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.private & host_chat
                   & Filters.command(["unblock"], glovar.prefix))
def unblock(client, message):
    try:
        hid = message.from_user.id
        mid = message.message_id
        _, cid = get_guest(message)
        if cid:
            if cid in glovar.blacklist_ids:
                remove_id(cid, 0, "blacklist")
                text = (f"用户 ID：{user_mention(cid)}\n"
                        f"状态：{code('已解禁')}\n")
            else:
                text = (f"用户 ID：{user_mention(cid)}\n"
                        f"状态：{code('操作失败')}\n"
                        f"原因：{code('该用户不在黑名单中')}\n")

            thread(send_message, (client, hid, text, mid))
        elif len(message.command) == 2:
            try:
                cid = int(message.command[1])
            except Exception as e:
                text = (f"格式有误\n"
                        f"{code_block(e)}\n")
                thread(send_message, (client, hid, text, mid))
                return

            remove_id(cid, 0, "blacklist")
            text = (f"用户 ID：{user_mention(cid)}\n"
                    f"状态：{code('已解禁')}\n")
            thread(send_message, (client, hid, text, mid))
        else:
            text = "如需解禁某人，请回复某条包含该用户 ID 的汇报消息\n"
            thread(send_message, (client, hid, text, mid))
    except Exception as e:
        logger.warning(f"Unblock error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & test_group
                   & Filters.command(["version"], glovar.prefix))
def version(client, message):
    try:
        cid = message.chat.id
        aid = message.from_user.id
        mid = message.message_id
        text = (f"管理员：{user_mention(aid)}\n\n"
                f"版本：{bold(glovar.version)}\n")
        thread(send_message, (client, cid, text, mid))
    except Exception as e:
        logger.warning(f"Version error: {e}", exc_info=True)
