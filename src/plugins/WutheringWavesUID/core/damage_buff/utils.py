# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage_buff/utils.py
# (迁移自 WutheringWavesUID1/utils/map/damage/utils.py)

import json
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any

# 适配修改：路径指向 core/data/
DATA_PATH = Path(__file__).parent.parent / "data"
CHAR_ID_MAP_PATH = DATA_PATH / "CharId2Data.json"


@lru_cache
def get_char_id_map() -> Dict[str, Any]:
    with open(CHAR_ID_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_char_info_by_id(char_id: int) -> Dict[str, Any]:
    return get_char_id_map().get(str(char_id), {})


def get_weapon_info_by_id(weapon_id: int) -> Dict[str, Any]:
    # 适配修改：武器数据也在 CharId2Data.json 中
    return get_char_id_map().get(str(weapon_id), {})


CALC_PERCENT = {
    "15": "湮灭伤害加成",
    "16": "衍射伤害加成",
    "17": "气动伤害加成",
    "18": "导电伤害加成",
    "19": "热熔伤害加成",
    "20": "冷凝伤害加成",
}

CHAR_ATTR_SINKING = "湮灭"
CHAR_ATTR_CELESTIAL = "衍射"
CHAR_ATTR_SIERRA = "气动"
CHAR_ATTR_VOID = "导电"
CHAR_ATTR_MOLTEN = "热熔"
CHAR_ATTR_FREEZING = "冷凝"

SONATA_GROUP = {
    1001: "不绝余音",
    1002: "凝夜白霜",
    1003: "熔山裂谷",
    1004: "彻空冥雷",
    1005: "啸谷长风",
    1006: "浮星祛暗",
    1007: "沉日劫明",
    1008: "隐世回光",
    1009: "轻云出月",
}

temp_atk = 1
temp_def = 2
temp_hp = 3
temp_heal = 4
temp_crit = 5
temp_crit_dmg = 6

normal_damage = 1
hit_damage = 2
skill_damage = 3
liberation_damage = 4