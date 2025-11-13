# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/ascension/weapon.py
import json
from functools import lru_cache
from pathlib import Path
from typing import List

from .constant import WEAPON_MAX_LEVEL
from .model import AscensionWeapon, WeaponAscensionData
from .template import AscensionTemplate

# 适配修改：从 from utils.map.detail_json...
JSON_PATH = Path(__file__).parent.parent / "data" / "detail_json" / "weapon"


@lru_cache
def _get_weapon_ascension_data(weapon_id: str) -> WeaponAscensionData:
    with open(JSON_PATH / f"{weapon_id}.json", "r", encoding="utf-8") as f:
        return json.load(f)


class WeaponAscension(AscensionTemplate[AscensionWeapon]):
    def __init__(self, weapon_id: str) -> None:
        data = _get_weapon_ascension_data(weapon_id)
        super().__init__(data["ascensions"], data["levels"])
        self.weapon_id = weapon_id

    def get_val_by_level(self, level: int, promote_level: int) -> List[float]:
        return self.levels[promote_level][level - 1]