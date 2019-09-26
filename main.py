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
from plugins.functions.timers import interval_min, interval_sec, reset_data, reset_direct, update_status

# Enable logging
logger = logging.getLogger(__name__)

# Config session
app = Client(
    session_name="bot",
    bot_token=glovar.bot_token
)
app.start()

# Timer
scheduler = BackgroundScheduler()
scheduler.add_job(interval_sec, "interval", seconds=glovar.flood_time)
scheduler.add_job(interval_min, "interval", minutes=glovar.flood_ban)

# Work with other bots
if glovar.exchange_channel_id:
    # Send online status
    update_status(app, "online")
    # Report status every hour
    scheduler.add_job(update_status, "cron", [app, "awake"], minute=30)

scheduler.add_job(reset_direct, "cron", hour=18)
scheduler.add_job(reset_data, "cron", day=glovar.reset_day, hour=22)
scheduler.start()

# Hold
app.idle()

# Stop
app.stop()
