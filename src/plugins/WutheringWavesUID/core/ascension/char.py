# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/ascension/char.py
import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

from .constant import CHAR_MAX_LEVEL
from .model import AscensionChar, CharAscensionData
from .template import AscensionTemplate

# 适配修改：从 from utils.map.detail_json...
JSON_PATH = Path(__file__).parent.parent / "data" / "detail_json" / "char"


@lru_cache
def _get_char_ascension_data(char_id: str) -> CharAscensionData:
    with open(JSON_PATH / f"{char_id}.json", "r", encoding="utf-8") as f:
        return json.load(f)


class CharAscension(AscensionTemplate[AscensionChar]):
    def __init__(self, char_id: str) -> None:
        data = _get_char_ascension_data(char_id)
        super().__init__(data["ascensions"], data["levels"])
        self.char_id = char_id

    def get_extra_val(self, promote_level: int) -> Dict[str, float]:
        return self.data[promote_level]["extra_val"]

    def get_total_extra_val(self, promote_level: int) -> Dict[str, float]:
        extra_val = {}
        for i in range(promote_level + 1):
            for k, v in self.get_extra_val(i).items():
                extra_val[k] = extra_val.get(k, 0) + v
        return extra_val

    def get_val_by_level(self, level: int, promote_level: int) -> List[float]:
        return self.levels[promote_level][level - 1]