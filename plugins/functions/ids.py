import logging

from .. import glovar
from ..functions.files import save

# Enable logging
logger = logging.getLogger(__name__)


def add_id(cid, mid, ctx):
    try:
        init_id(cid)
        if ctx == "blacklist":
            if cid not in glovar.blacklist_ids:
                glovar.blacklist_ids.add(cid)
                save("blacklist_ids")
        elif ctx == "flood":
            if cid not in glovar.flood_ids["users"]:
                glovar.flood_ids["users"].add(cid)
        elif ctx in {"from", "to"}:
            if mid not in glovar.message_ids[cid][ctx]:
                glovar.message_ids[cid][ctx].add(mid)
                save("message_ids")
    except Exception as e:
        logger.warning(f"Add {ctx} id error: {e}", exc_info=True)


def clear_counts():
    try:
        glovar.flood_ids["counts"] = {}
    except Exception as e:
        logger.warning(f"Clear counts error: {e}", exc_info=True)


def clear_flood():
    try:
        glovar.flood_ids["users"] = set()
    except Exception as e:
        logger.warning(f"Clear flood users error: {e}", exc_info=True)


def count_id(cid: int) -> int:
    try:
        init_id(cid)
        glovar.flood_ids["counts"][cid] += 1
        return glovar.flood_ids["counts"][cid]
    except Exception as e:
        logger.warning(f"Count id error: {e}", exc_info=True)


def init_id(cid):
    try:
        if glovar.flood_ids["counts"].get(cid) is None:
            glovar.flood_ids["counts"][cid] = 0

        if glovar.message_ids.get(cid) is None:
            glovar.message_ids[cid] = {
                "from": set(),
                "to": set()
            }
    except Exception as e:
        logger.warning(f"Init id error: {e}", exc_info=True)


def remove_id(cid, mid, ctx):
    try:
        init_id(cid)
        if ctx == "blacklist":
            if cid in glovar.blacklist_ids:
                glovar.blacklist_ids.remove(cid)
                save("blacklist_ids")
        elif ctx == "cat_to":
            glovar.message_ids[cid]["to"] = set()
            save("message_ids")
        elif ctx == "chat_all":
            glovar.message_ids.pop(cid)
            save("message_ids")
        elif ctx == "to":
            if mid in glovar.message_ids[cid]["to"]:
                glovar.message_ids[cid]["to"].remove(mid)
                save("message_ids")
    except Exception as e:
        logger.warning(f"Remove {ctx} id error: {e}", exc_info=True)
