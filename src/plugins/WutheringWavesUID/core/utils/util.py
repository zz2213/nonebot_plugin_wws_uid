# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/utils/util.py

from typing import Dict


MY_SYNC_S = ["uid", "user_id", "platform", "channel"]


def sync_dict(old: Dict, new: Dict, key: list = MY_SYNC_S):
    for i in key:
        if i in old:
            new[i] = old[i]