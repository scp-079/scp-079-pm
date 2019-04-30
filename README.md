# SCP-079-PM

Everyone can have their own Telegram private chat bot.

This project provides python code of a Telegram private chat forwarding bot.

## How to use

See [this article](https://scp-079.org/pm/).

## To Do List

- [x] Complete basic functions
- [x] Recall single message
- [x] Error report
- [x] Recall all messages
- [x] Add blacklist feature
- [x] Anti-flood
- [x] Add reply-to feature
- [x] Chat directly with someone
- [x] Support editing message text

## Requirements

- Python 3.6 or higher
- `requirements.txt` : APScheduler pyrogram[fast]

## Files

- plugins
    - functions
        - `deliver.py` : I am a postman
        - `etc.py` : Miscellaneous
        - `file.py` : Save files
        - `filters.py` : Some filters
        - `ids.py` : Modify id lists
        - `telegram.py` : Some telegram functions
        - `timers.py` : Timer functions
    - handlers
        - `callback.py` : Handle callbacks
        - `command.py` : Handle commands
        - `message.py` : Handle messages
    - `glovar.py` : Global variables
- `.gitignore` : Ignore
- `config.ini.example` -> `config.ini` : Configures
- `LICENSE` : GPLv3
- `main.py` : Start here
- `README.md` : This file
- `requirements.txt` : Managed by pip

## Contribute

Welcome to make this project even better. You can submit merge requests, or report issues.

## License

Licensed under the terms of the [GNU General Public License v3](LICENSE).
