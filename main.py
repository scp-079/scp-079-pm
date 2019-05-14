#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

from apscheduler.schedulers.background import BackgroundScheduler
from pyrogram import Client

from plugins import glovar
from plugins.functions.timers import clear_counts, clear_flood, update_status

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
    filename='log',
    filemode='w'
)

logger = logging.getLogger(__name__)

# Start
app = Client(
    session_name="bot",
    bot_token=glovar.bot_token
)
app.start()

# Timer
scheduler = BackgroundScheduler()
if glovar.exchange_channel_id:
    scheduler.add_job(update_status, "cron", [app], minute=30)

scheduler.add_job(clear_counts, 'interval', seconds=5)
scheduler.add_job(clear_flood, "interval", minutes=15)
scheduler.start()

# Hold
app.idle()
