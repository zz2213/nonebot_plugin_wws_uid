# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/ascension/sonata.py
import json
from functools import lru_cache
from pathlib import Path
from typing import List

from .model import AscensionSonata, SonataAscensionData
from .template import AscensionTemplate

# 适配修改：从 from utils.map.detail_json...
JSON_PATH = Path(__file__).parent.parent / "data" / "detail_json" / "sonata"


@lru_cache
def _get_sonata_ascension_data(name: str) -> SonataAscensionData:
    with open(JSON_PATH / f"{name}.json", "r", encoding="utf-8") as f:
        return json.load(f)


class SonataAscension(AscensionTemplate[AscensionSonata]):
    def __init__(self, name: str) -> None:
        data = _get_sonata_ascension_data(name)
        super().__init__(data["ascensions"], [])
        self.name = name

    def get_effect(self, active_num: int) -> str:
        for asc in self.data:
            if asc["active_num"] == active_num:
                return asc["effect"]
        return ""