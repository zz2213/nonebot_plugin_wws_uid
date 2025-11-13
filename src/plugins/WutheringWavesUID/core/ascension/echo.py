# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/ascension/echo.py
import json
from functools import lru_cache
from pathlib import Path
from typing import List

from .constant import ECHO_MAX_LEVEL
from .model import AscensionEcho, EchoAscensionData
from .template import AscensionTemplate

# 适配修改：从 from utils.map.detail_json...
JSON_PATH = Path(__file__).parent.parent / "data" / "detail_json" / "echo"


@lru_cache
def _get_echo_ascension_data(rarity: str) -> EchoAscensionData:
    with open(JSON_PATH / f"{rarity}.json", "r", encoding="utf-8") as f:
        return json.load(f)


class EchoAscension(AscensionTemplate[AscensionEcho]):
    def __init__(self, rarity: str) -> None:
        data = _get_echo_ascension_data(rarity)
        super().__init__(data["ascensions"], data["levels"])
        self.rarity = rarity

    def get_cost(self, level: int) -> int:
        return self.data[level - 1]["cost"]

    def get_total_cost(self, level: int) -> int:
        cost = 0
        for i in range(level):
            cost += self.get_cost(i + 1)
        return cost

    def get_val_by_level(self, level: int) -> List[float]:
        return self.levels[0][level - 1]