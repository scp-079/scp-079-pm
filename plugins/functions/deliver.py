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
from functools import partial
from typing import Optional

from pyrogram import Client, InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import FloodWait, UserIsBlocked

from .. import glovar
from .etc import button_data, code, code_block, get_text, name_mention, thread, user_mention, wait_flood
from .file import save
from .ids import init_id, remove_id
from .ids import add_id, reply_id
from .telegram import delete_messages, send_message

# Enable logging
logger = logging.getLogger(__name__)


def clear_data(data_type: str) -> str:
    # Clear stored data
    text = ""
    try:
        if data_type == "messages":
            glovar.message_ids = {}
            save("message_ids")
            glovar.reply_ids = {
                "g2h": {},
                "h2g": {}
            }
            save("reply_ids")
            text += f"已清空：{code('消息 ID')}\n"
        else:
            glovar.blacklist_ids = set()
            save("blacklist_ids")
            text += f"已清空：{code('黑名单')}\n"
    except Exception as e:
        logger.warning(f"Clear data error: {e}", exc_info=True)
        text += (f"未清空：{code('出现错误')}\n"
                 f"错误：\n\n"
                 f"{code_block(e)}\n")

    return text


def forward(
    self,
    chat_id: int or str,
    disable_notification: bool = None,
    as_copy: bool = False,
    remove_caption: bool = False,
    reply_to_message_id: int = None
) -> "Message":
    # Redefine the "forward" bound method of "Message", see:
    # https://github.com/pyrogram/pyrogram/blob/develop/pyrogram/client/types/messages_and_media/message.py#L2558
    if as_copy:
        if self.service:
            raise ValueError("Unable to copy service messages")

        if self.game and not self._client.is_bot:
            raise ValueError("Users cannot send messages with Game media type")

        if self.text:
            return self._client.send_message(
                chat_id,
                text=self.text.html,
                parse_mode="html",
                disable_web_page_preview=not self.web_page,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id
            )
        elif self.media:
            caption = self.caption.html if self.caption and not remove_caption else ""

            send_media = partial(
                self._client.send_cached_media,
                chat_id=chat_id,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id
            )

            if self.photo:
                file_id = self.photo.file_id
            elif self.audio:
                file_id = self.audio.file_id
            elif self.document:
                file_id = self.document.file_id
            elif self.video:
                file_id = self.video.file_id
            elif self.animation:
                file_id = self.animation.file_id
            elif self.voice:
                file_id = self.voice.file_id
            elif self.sticker:
                file_id = self.sticker.file_id
            elif self.video_note:
                file_id = self.video_note.file_id
            elif self.contact:
                return self._client.send_contact(
                    chat_id,
                    phone_number=self.contact.phone_number,
                    first_name=self.contact.first_name,
                    last_name=self.contact.last_name,
                    vcard=self.contact.vcard,
                    disable_notification=disable_notification,
                    reply_to_message_id=reply_to_message_id
                )
            elif self.location:
                return self._client.send_location(
                    chat_id,
                    latitude=self.location.latitude,
                    longitude=self.location.longitude,
                    disable_notification=disable_notification,
                    reply_to_message_id=reply_to_message_id
                )
            elif self.venue:
                return self._client.send_venue(
                    chat_id,
                    latitude=self.venue.location.latitude,
                    longitude=self.venue.location.longitude,
                    title=self.venue.title,
                    address=self.venue.address,
                    foursquare_id=self.venue.foursquare_id,
                    foursquare_type=self.venue.foursquare_type,
                    disable_notification=disable_notification,
                    reply_to_message_id=reply_to_message_id
                )
            elif self.poll:
                return self._client.send_poll(
                    chat_id,
                    question=self.poll.question,
                    options=[opt.text for opt in self.poll.options],
                    disable_notification=disable_notification,
                    reply_to_message_id=reply_to_message_id
                )
            elif self.game:
                return self._client.send_game(
                    chat_id,
                    game_short_name=self.game.short_name,
                    disable_notification=disable_notification,
                    reply_to_message_id=reply_to_message_id
                )
            else:
                raise ValueError("Unknown media type")

            if self.sticker or self.video_note:  # Sticker and VideoNote should have no caption
                return send_media(file_id=file_id)
            else:
                return send_media(file_id=file_id, caption=caption, parse_mode="html")
        else:
            raise ValueError("Can't copy this message")
    else:
        return self._client.forward_messages(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_ids=self.message_id,
            disable_notification=disable_notification,
        )


def deliver_guest_message(client: Client, message: Message) -> bool:
    # Deliver guest message to host chat
    try:
        hid = glovar.host_id
        cid = message.chat.id
        mid = message.message_id
        result = deliver_message(client, message, hid, mid, "g2h")
        if result and isinstance(result, Message) and not result.edit_date:
            text = (f"用户 ID：{code(cid)}\n"
                    f"昵称：{name_mention(message.from_user)}\n")
            if message.edit_date:
                text += f"类别：{code('已编辑')}\n"

            forward_mid = result.message_id
            thread(send_message, (client, hid, text, forward_mid))
            # Record the message's id
            add_id(cid, mid, "guest")
            reply_id(mid, forward_mid, cid, "guest")
            reply_id(forward_mid, mid, cid, "host")
            return True
    except Exception as e:
        logger.warning(f"Deliver guest message error: {e}", exc_info=True)

    return False


def deliver_host_message(client: Client, message: Message, cid: int) -> bool:
    # Deliver host message to guest chat
    try:
        hid = glovar.host_id
        mid = message.message_id
        if cid not in glovar.blacklist_ids:
            result = deliver_message(client, message, cid, mid, "h2g")
            if result and isinstance(result, Message) and not result.edit_date:
                text = (f"发送至 ID：{user_mention(cid)}\n"
                        f"状态：{code('已发送')}\n")
                forward_mid = result.message_id
                data = button_data("recall", "single", forward_mid)
                markup = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "撤回",
                                callback_data=data
                            )
                        ]
                    ]
                )
                thread(send_message, (client, hid, text, mid, markup))
                # Record the message's id
                add_id(cid, forward_mid, "host")
                reply_id(mid, forward_mid, cid, "host")
                reply_id(forward_mid, mid, cid, "guest")
                return True
        else:
            text = (f"发送至 ID：{user_mention(cid)}\n"
                    f"状态：{code('发送失败')}\n"
                    f"原因：{code('该用户在黑名单中')}\n")
            thread(send_message, (client, hid, text, mid))
    except Exception as e:
        logger.warning(f"Deliver host message error: {e}", exc_info=True)

    return False


def deliver_fail(client: Client, cid: int, mid: int) -> bool:
    # Send a report message when deliver failed
    try:
        text = (f"状态：{code('发送失败')}\n"
                f"原因：{code('对方已停用机器人')}\n")
        thread(send_message, (client, cid, text, mid))
        return True
    except Exception as e:
        logger.warning(f"Deliver fail error: {e}", exc_info=True)

    return False


def deliver_message(client: Client, message: Message,
                    chat_id: int, message_id: int, reply_type: str) -> Optional[Message]:
    # Deliver a message to guest or host
    result = None
    try:
        # If message is forwarded from someone else, bot directly forward this message, not using as copy mode
        if message.forward_from or message.forward_from_chat or message.forward_sender_name:
            as_copy = False
        else:
            as_copy = True

        # Temporary for animated stickers
        if not (message.text or message.media):
            as_copy = False

        # Check to see if the bot knows which message shall be replied to
        reply_mid = None
        if message.reply_to_message:
            reply_mid = message.reply_to_message.message_id
            reply_mid = glovar.reply_ids[reply_type].get(reply_mid, (None, None))[0]

        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                # If message is not edited, directly send it
                if not message.edit_date:
                    if as_copy:
                        result = forward(
                            self=message,
                            chat_id=chat_id,
                            as_copy=True,
                            reply_to_message_id=reply_mid
                        )
                    else:
                        result = message.forward(chat_id=chat_id)
                else:
                    # If message is edited, check to see if the bot knows which message is corresponding
                    origin_mid = glovar.reply_ids[reply_type].get(message_id, (None, None))[0]
                    if chat_id != glovar.host_id and origin_mid and message.text:
                        result = client.edit_message_text(
                            chat_id=chat_id,
                            message_id=origin_mid,
                            text=message.text
                        )
                    # Guest's edited message / Can't find origin message / Not a text message, so bot resend the message
                    else:
                        result = forward(
                            self=message,
                            chat_id=chat_id,
                            as_copy=as_copy,
                            reply_to_message_id=origin_mid
                        )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except UserIsBlocked:
                # If the other user blocked the bot, send a failure report to who sent the message
                deliver_fail(client, message.from_user.id, message_id)
                return None
            except Exception as e:
                logger.warning(f"Forward message error: {e}", exc_info=True)
                return None
    except Exception as e:
        logger.warning(f"Deliver message error: {e}", exc_info=True)

    return result


def get_guest(message: Message) -> (int, int):
    # Get a guest chat id
    mid = 0
    cid = 0
    try:
        r_message = message.reply_to_message
        message_text = get_text(r_message)
        if r_message:
            # Check if the replied message is a valid report message
            if (r_message.from_user.is_self
                    and "ID" in message_text
                    and len(message_text.split("\n")) > 1):
                cid = int(message_text.partition("\n")[0].partition("ID")[2][1:])
            # Else check to see if bot knows which message is corresponding
            elif glovar.reply_ids["h2g"].get(r_message.message_id, (None, None))[0]:
                mid = glovar.reply_ids["h2g"][r_message.message_id][0]
                cid = glovar.reply_ids["h2g"][r_message.message_id][1]
    except Exception as e:
        logger.warning(f"Get guest error: {e}", exc_info=True)

    return mid, cid


def recall_messages(client: Client, cid: int, recall_type: str, recall_mid: int) -> str:
    # Recall messages in a chat
    text = f"对话 ID：{user_mention(cid)}\n"
    try:
        init_id(cid)
        # Recall single message
        if recall_type == "single":
            thread(delete_messages, (client, cid, [recall_mid]))
            remove_id(cid, recall_mid, "host")
            text += f"状态：{code('已撤回')}\n"
        # Recall all host's messages
        elif recall_type == "host":
            if glovar.message_ids[cid]["host"]:
                thread(delete_messages, (client, cid, glovar.message_ids[cid]["host"]))
                remove_id(cid, 0, "chat_host")
                text += f"状态：{code('已撤回由您发送的全部消息')}\n"
            else:
                text += f"状态：{code('没有可撤回的消息')}\n"
        # Recall all messages in a guest's chat
        else:
            if glovar.message_ids[cid]["host"] or glovar.message_ids[cid]["guest"]:
                if glovar.message_ids[cid]["host"]:
                    thread(delete_messages, (client, cid, glovar.message_ids[cid]["host"]))

                if glovar.message_ids[cid]["guest"]:
                    thread(delete_messages, (client, cid, glovar.message_ids[cid]["guest"]))

                remove_id(cid, 0, "chat_all")
                text += f"状态：{code('已撤回全部消息')}\n"
            else:
                text += f"状态：{code('没有可撤回的消息')}\n"
    except Exception as e:
        logger.warning(f"Recall message error: {e}", exc_info=True)
        text += (f"状态：{code('出现错误')}\n"
                 f"错误：\n\n"
                 f"{code_block(e)}\n")

    return text
