# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/utils/scoring.py

import json
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Tuple

# 适配修改：路径指向 core/data/
DATA_PATH = Path(__file__).parent.parent / "data"
ID_NAME_PATH = DATA_PATH / "id2name.json"
CALC_SCRIPT_PATH = DATA_PATH / "calc_score_script.py"  # 源文件
LIMIT_PATH = DATA_PATH / "limit.json"


@lru_cache
def get_id_name_map() -> dict:
  """加载 id2name.json 数据"""
  try:
    with open(ID_NAME_PATH, "r", encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    return {}


@lru_cache
def get_limit_data() -> dict:
  """加载 limit.json 数据"""
  try:
    with open(LIMIT_PATH, "r", encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    return {}


# --- 以下代码迁移自 WutheringWavesUID1/utils/map/calc_score_script.py ---

# 评分等级
SCORE_LEVELS = {
  "SSS": 60,
  "SS": 50,
  "S": 40,
  "A": 30,
  "B": 20,
  "C": 0,
}

# 角色词条权重
# 适配修改：移除了原文件的动态加载，直接写入
CHAR_SCORE_PERS = {
  "1102": ["暴击", "暴击伤害", "攻击", "共鸣技能伤害加成", "共鸣解放伤害加成"],  # 散华
  "1103": ["治疗效果加成", "共鸣效率", "生命", "防御"],  # 白芷
  "1104": ["暴击", "暴击伤害", "攻击", "冷凝伤害加成", "普攻伤害加成"],  # 凌阳
  "1105": ["暴击", "暴击伤害", "攻击", "冷凝伤害加成", "普攻伤害加成"],  # 折枝 (假设)
  "1106": ["防御", "共鸣效率", "治疗效果加成"],  # 釉瑚
  "1107": ["暴击", "暴击伤害", "攻击", "热熔伤害加成", "共鸣技能伤害加成"],  # 珂莱塔 (假设)
  "1202": ["暴击", "暴击伤害", "攻击", "热熔伤害加成", "普攻伤害加成"],  # 炽霞
  "1203": ["暴击", "暴击伤害", "攻击", "热熔伤害加成", "共鸣技能伤害加成"],  # 安可
  "1204": ["共鸣效率", "攻击", "热熔伤害加成"],  # 莫特斐
  "1205": ["暴击", "暴击伤害", "攻击", "热熔伤害加成", "普攻伤害加成"],  # 长离
  "1301": ["暴击", "暴击伤害", "攻击", "导电伤害加成", "共鸣解放伤害加成"],  # 卡卡罗
  "1302": ["暴击", "暴击伤害", "攻击", "导电伤害加成", "共鸣效率"],  # 吟霖
  "1303": ["暴击", "暴击伤害", "攻击", "导电伤害加成", "生命"],  # 渊武
  "1304": ["暴击", "暴击伤害", "攻击", "衍射伤害加成", "共鸣解放伤害加成"],  # 今汐 (假设)
  "1402": ["共鸣效率", "攻击", "气动伤害加成"],  # 秧秧
  "1403": ["暴击", "暴击伤害", "攻击", "气动伤害加成"],  # 秋水 (假设)
  "1404": ["暴击", "暴击伤害", "攻击", "气动伤害加成", "重击伤害加成"],  # 忌炎
  "1405": ["暴击", "暴击伤害", "攻击", "气动伤害加成", "共鸣效率"],  # 鉴心
  "1406": ["暴击", "暴击伤害", "攻击", "气动伤害加成", "共鸣技能伤害加成"],  # 漂泊者·气动
  "1408": ["暴击", "暴击伤害", "攻击", "气动伤害加成", "共鸣技能伤害加成"],  # 漂泊者·气动
  "1501": ["暴击", "暴击伤害", "攻击", "衍射伤害加成", "共鸣技能伤害加成"],  # 漂泊者·衍射
  "1502": ["暴击", "暴击伤害", "攻击", "衍射伤害加成", "共鸣技能伤害加成"],  # 漂泊者·衍射
  "1503": ["治疗效果加成", "共鸣效率", "攻击", "生命"],  # 维里奈
  "1504": ["暴击", "暴击伤害", "攻击", "衍射伤害加成"],  # 灯灯 (假设)
  "1601": ["防御", "共鸣效率", "治疗效果加成"],  # 桃祈
  "1602": ["暴击", "暴击伤害", "攻击", "湮灭伤害加成", "普攻伤害加成"],  # 丹瑾
  "1603": ["暴击", "暴击伤害", "生命", "湮灭伤害加成", "共鸣技能伤害加成"],  # 椿 (假设)
  "1604": ["暴击", "暴击伤害", "攻击", "湮灭伤害加成", "共鸣技能伤害加成"],  # 漂泊者·湮灭
  "1605": ["暴击", "暴击伤害", "攻击", "湮灭伤害加成", "共鸣技能伤害加成"],  # 漂泊者·湮灭
  "default": ["暴击", "暴击伤害", "攻击", "共鸣技能伤害加成", "共鸣解放伤害加成"],
}

# 词条分数
ATTR_SCORE = {
  "暴击": 2.5,
  "暴击伤害": 2.5,
  "攻击": 1.6666,
  "攻击力": 1.6666,
  "生命": 1.6666,
  "生命值": 1.6666,
  "防御": 1.6666,
  "防御力": 1.6666,
  "共鸣效率": 1.6666,
  "冷凝伤害加成": 2.5,
  "热熔伤害加成": 2.5,
  "导电伤害加成": 2.5,
  "气动伤害加成": 2.5,
  "衍射伤害加成": 2.5,
  "湮灭伤害加成": 2.5,
  "普攻伤害加成": 2.0,
  "重击伤害加成": 2.0,
  "共鸣技能伤害加成": 2.0,
  "共鸣解放伤害加成": 2.0,
  "治疗效果加成": 2.0,
}


def get_char_score_pers(char_id: str) -> List[str]:
  """获取角色的推荐词条"""
  return CHAR_SCORE_PERS.get(str(char_id), CHAR_SCORE_PERS["default"])


def get_score_level(score: float) -> str:
  """根据分数获取等级"""
  for level, min_score in SCORE_LEVELS.items():
    if score >= min_score:
      return level
  return "C"


def calc_score(main_attr: str, sub_attrs: List[Dict], char_id: str = "default") -> Tuple[float, float, int]:
  """
  计算声骸得分
  :param main_attr: 主词条名称 (e.g., "暴击")
  :param sub_attrs: 副词条列表 (e.g., [{"key": "攻击", "value": 10.0}])
  :param char_id: 角色ID
  :return: (总分, 主词条分, 命中词条数)
  """
  id_name_map = get_id_name_map()
  limit_data = get_limit_data()

  # 查找主词条的标准名称
  main_key = id_name_map.get(main_attr, main_attr)

  # 获取角色推荐词条
  char_pers = get_char_score_pers(str(char_id))

  # 获取词条的理论最大值 (5级)
  max_limit = limit_data.get("5", {})

  total_score = 0.0
  main_score = 0.0
  hit_count = 0

  # 1. 计算主词条得分
  if main_key in char_pers and main_key in ATTR_SCORE:
    # 主词条满分固定为 15
    total_score += 15
    main_score = 15
    hit_count += 1
  elif "cost 4" in main_key and main_key.replace("cost 4", "").strip() in ATTR_SCORE:
    # 适配 "cost 4 暴击" 这种情况
    main_key_cleaned = main_key.replace("cost 4", "").strip()
    if main_key_cleaned in char_pers:
      total_score += 15
      main_score = 15
      hit_count += 1

  # 2. 计算副词条得分
  for item in sub_attrs:
    sub_key = id_name_map.get(item.get("key"), item.get("key"))
    sub_value = item.get("value", 0.0)

    # 确保 value 是浮点数
    try:
      sub_value = float(sub_value)
    except (ValueError, TypeError):
      sub_value = 0.0

    if sub_key in char_pers and sub_key in ATTR_SCORE:
      hit_count += 1
      # 获取该词条的理论最大值
      max_val = max_limit.get(sub_key, 0)
      if max_val > 0:
        # 得分 = (实际值 / 理论最大值) * 单词条满分 (10分) * 权重 (e.g., 暴击2.5)
        # (原项目的算法)
        total_score += (sub_value / max_val) * ATTR_SCORE[sub_key] * 10 / 2.5
      else:
        # 降级处理 (如果 limit.json 缺失)
        total_score += ATTR_SCORE[sub_key]

  return round(total_score, 1), round(main_score, 1), hit_count