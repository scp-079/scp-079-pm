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
from time import sleep
from typing import Iterable, Union

import pyrogram
from pyrogram import Client, InlineKeyboardButton, InlineKeyboardMarkup, Message, ParseMode
from pyrogram.api import functions, types
from pyrogram.errors import FloodWait, UserIsBlocked

from .. import glovar
from .etc import button_data, code, thread, user_mention
from .ids import add_id, reply_id
from .telegram import send_message

# Enable logging
logger = logging.getLogger(__name__)


def forward_messages(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_ids: Iterable[int],
        disable_notification: bool = None,
        as_copy: bool = False,
        remove_caption: bool = False,
        reply_to_message_id: int = None
) -> "pyrogram.Messages":
    is_iterable = not isinstance(message_ids, int)
    message_ids = list(message_ids) if is_iterable else [message_ids]

    if as_copy:
        forwarded_messages = []

        for chunk in [message_ids[i:i + 200] for i in range(0, len(message_ids), 200)]:
            messages = self.get_messages(chat_id=from_chat_id, message_ids=chunk)  # type: pyrogram.Messages

            for message in messages.messages:
                forwarded_messages.append(
                    message.forward(
                        chat_id,
                        disable_notification=disable_notification,
                        as_copy=True,
                        remove_caption=remove_caption,
                        reply_to_message_id=reply_to_message_id
                    )
                )

        return pyrogram.Messages(
            client=self,
            total_count=len(forwarded_messages),
            messages=forwarded_messages
        ) if is_iterable else forwarded_messages[0]
    else:
        r = self.send(
            functions.messages.ForwardMessages(
                to_peer=self.resolve_peer(chat_id),
                from_peer=self.resolve_peer(from_chat_id),
                id=message_ids,
                silent=disable_notification or None,
                random_id=[self.rnd_id() for _ in message_ids]
            )
        )

        forwarded_messages = []

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for i in r.updates:
            if isinstance(i, (types.UpdateNewMessage, types.UpdateNewChannelMessage)):
                forwarded_messages.append(
                    pyrogram.Message._parse(
                        self, i.message,
                        users, chats
                    )
                )

        return pyrogram.Messages(
            client=self,
            total_count=len(forwarded_messages),
            messages=forwarded_messages
        ) if is_iterable else forwarded_messages[0]


def forward(
        self,
        chat_id: int or str,
        disable_notification: bool = None,
        as_copy: bool = False,
        remove_caption: bool = False,
        reply_to_message_id: int = None
) -> "Message":
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
            caption = self.caption.html if self.caption and not remove_caption else None

            send_media = partial(
                self._client.send_cached_media,
                chat_id=chat_id,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id
            )

            if self.photo:
                file_id = self.photo.sizes[-1].file_id
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
                return send_media(file_id=file_id, caption=caption, parse_mode=ParseMode.HTML)
        else:
            raise ValueError("Can't copy this message")
    else:
        return self._client.forward_messages(
            chat_id=chat_id,
            from_chat_id=self.chat.id,
            message_ids=self.message_id,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id
        )


pyrogram.Client.forward_messages = forward_messages
pyrogram.Message.forward = forward


def deliver_guest_message(client: Client, message: Message) -> bool:
    try:
        hid = glovar.host_id
        cid = message.chat.id
        mid = message.message_id
        mids = [mid]
        if message.forward_from or message.forward_from_chat or message.forward_from_name:
            as_copy = False
        else:
            as_copy = True

        result = None
        while not result:
            try:
                result = client.forward_messages(
                    chat_id=hid,
                    from_chat_id=cid,
                    message_ids=mids,
                    disable_notification=True,
                    as_copy=as_copy
                )
            except FloodWait as e:
                sleep(e.x + 1)
            except UserIsBlocked:
                deliver_fail(client, cid, mid)
                return False
            except Exception as e:
                logger.warning(f"Forward message error: {e}")
                return False

        text = (f"用户 ID：{code(cid)}\n"
                f"昵称：[{message.from_user.first_name}](tg://user?id={cid})")
        forward_mid = result.messages[0].message_id
        thread(send_message, (client, hid, text, forward_mid))
        add_id(cid, mid, "guest")
        reply_id(mid, forward_mid, cid, "guest")
        return True
    except Exception as e:
        logger.warning(f"Deliver guest message error: {e}", exc_info=True)

    return False


def deliver_host_message(client: Client, message: Message, cid: int) -> bool:
    try:
        hid = glovar.host_id
        mid = message.message_id
        mids = [mid]
        if cid not in glovar.blacklist_ids:
            if message.forward_from or message.forward_from_chat or message.forward_from_name:
                as_copy = False
            else:
                as_copy = True

            result = None
            while not result:
                try:
                    result = client.forward_messages(
                        chat_id=cid,
                        from_chat_id=hid,
                        message_ids=mids,
                        disable_notification=True,
                        as_copy=as_copy
                    )
                except FloodWait as e:
                    sleep(e.x + 1)
                except UserIsBlocked:
                    deliver_fail(client, hid, mid)
                    return False
                except Exception as e:
                    logger.warning(f"Forward message error: {e}")
                    return False

            text = (f"发送至 ID：[{cid}](tg://user?id={cid})\n"
                    f"状态：{code('已发送')}")
            forward_mid = result.messages[0].message_id
            data = button_data("recall", "single", str(forward_mid))
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
            add_id(cid, forward_mid, "host")
            reply_id(mid, forward_mid, cid, "host")
        else:
            text = (f"发送至 ID：{user_mention(cid)}\n"
                    f"状态：{code('发送失败')}\n"
                    f"原因：{code('该用户在黑名单中')}")
            thread(send_message, (client, hid, text, mid))

        return False
    except Exception as e:
        logger.warning(f"Deliver host message error: {e}", exc_info=True)

    return False


def deliver_fail(client: Client, cid: int, mid: int) -> bool:
    try:
        text = (f"状态：{code('发送失败')}\n"
                f"原因：{code('对方已停用机器人')}")
        thread(send_message, (client, cid, text, mid))
        return True
    except Exception as e:
        logger.warning(f"Deliver fail error: {e}", exc_info=True)

    return False


def get_guest(message: Message) -> int:
    try:
        r_message = message.reply_to_message
        if r_message:
            if (r_message.from_user.is_self
                    and "ID" in r_message.text
                    and len(r_message.text.split("\n")) > 1):
                cid = int(r_message.text.partition("\n")[0].partition("ID")[2][1:])
                return cid
    except Exception as e:
        logger.warning(f"Get guest error: {e}", exc_info=True)

    return 0
