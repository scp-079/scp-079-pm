import logging
from pickle import dump
from shutil import copyfile
from threading import Thread

from .. import glovar

# Enable logging
logger = logging.getLogger(__name__)


def save(ctx):
    t = Thread(target=save_thread, args=(ctx,))
    t.start()


def save_thread(ctx):
    try:
        if glovar:
            with open(f"data/.{ctx}", "wb") as f:
                dump(eval(f"glovar.{ctx}"), f)

            copyfile(f"data/.{ctx}", f"data/{ctx}")
    except Exception as e:
        logger.error(f"Save data error: {e}", exc_info=True)
