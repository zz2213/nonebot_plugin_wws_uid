# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/character_service.py

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from ..services.game_service import GameService
from ..core.api.waves_api import waves_api
from ..core.utils.scoring import calc_score, get_char_score_pers, get_id_name_map
from ..database import get_cache, set_cache

# --- 导入我们迁移的伤害计算框架 ---
from ..core.ascension.char import CharAscension
from ..core.ascension.weapon import WeaponAscension
from ..core.damage.damage import Damage
from ..core.damage.register_char import get_char as get_char_damage_func
from ..core.damage.register_weapon import get_weapon as get_weapon_damage_func
from ..core.damage.register_echo import get_echo as get_echo_damage_func

# --- 导入完成 ---


# 适配修改：路径指向 core/data/
DATA_PATH = Path(__file__).parent.parent / "core" / "data"
CHAR_DATA_PATH = DATA_PATH / "detail_json" / "char"
WEAPON_DATA_PATH = DATA_PATH / "detail_json" / "weapon"


class CharacterService:
  """
  角色数据处理服务
  (迁移自 char_info_utils.py, refresh_char_detail.py 并移除 gsuid_core 依赖)
  """

  def __init__(self, game_service: GameService):
    self.game_service = game_service
    self.id_name_map = get_id_name_map()

  def _get_name(self, key: str) -> str:
    """通过 id_name.json 获取标准名称"""
    return self.id_name_map.get(str(key), str(key))

  def _format_prop_data(self, prop_list: List[Dict]) -> Dict[str, float]:
    """
    格式化属性列表 (来自 char_info_utils.py)
    :param prop_list: 游戏 API 原始属性列表
    :return: 格式化后的 {属性名: 值} 字典
    """
    result = {}
    for prop in prop_list:
      prop_id = str(prop.get("id", ""))
      prop_name = self._get_name(prop_id)
      prop_value = float(prop.get("value", 0))

      if prop_name == "暴击":
        prop_name = "暴击率"

      # API 返回的百分比是小数，乘以 100
      if prop_id in [
        "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14",
        "15", "16", "17", "18", "19", "20", "21", "22", "23"
      ]:
        prop_value *= 100

      result[prop_name] = round(prop_value, 1)
    return result

  def _calc_echo_score(self, char_id: str, echo_list: List[Dict]) -> List[Dict]:
    """
    计算声骸得分 (来自 char_info_utils.py)
    :param char_id: 角色ID
    :param echo_list: 游戏 API 原始声骸列表
    :return: 附带得分和等级的声骸列表
    """
    processed_list = []
    total_score = 0.0

    for echo in echo_list:
      main_attr_key = echo.get("mainEntry", {}).get("key", "")
      sub_attr_list = echo.get("subEntry", [])

      sub_attrs = [
        {"key": self._get_name(s.get("key")), "value": s.get("value")}
        for s in sub_attr_list
      ]

      main_attr_name = self._get_name(main_attr_key)

      score, main_score, hit_count = calc_score(main_attr_name, sub_attrs, str(char_id))

      echo["score"] = score
      echo["mainScore"] = main_score
      echo["hitCount"] = hit_count
      echo["mainEntry"]["name"] = main_attr_name
      echo["subEntry"] = sub_attrs  # 覆盖为带 name 的列表

      processed_list.append(echo)
      total_score += score

    # 返回处理后的列表和总分
    return processed_list, total_score

  async def _refresh_char_detail(self, role_id: str, role_data: Dict) -> Dict:
    """
    使用伤害计算框架刷新角色详细属性 (来自 refresh_char_detail.py)
    :param role_id: 角色ID
    :param role_data: 游戏 API 原始角色数据
    :return: 包含详细计算属性的字典
    """
    char_id = str(role_id)

    # 1. 检查所需的数据文件是否存在
    char_json_path = CHAR_DATA_PATH / f"{char_id}.json"
    if not char_json_path.exists():
      return {"error": "缺少角色计算数据文件"}

    weapon_id = str(role_data.get("weapon", {}).get("id", 0))
    weapon_json_path = WEAPON_DATA_PATH / f"{weapon_id}.json"
    if not weapon_json_path.exists():
      return {"error": "缺少武器计算数据文件"}

    # 2. 加载角色的伤害计算框架
    try:
      char_asc_data = CharAscension(char_id).data
      weapon_asc_data = WeaponAscension(weapon_id).data
    except Exception as e:
      return {"error": f"加载突破数据失败: {e}"}

    # 3. 准备 Damage 类的输入
    damage_input = {
      "char_id": char_id,
      "char_level": role_data.get("level", 1),
      "char_promote_level": role_data.get("promoteLevel", 0),
      "char_chain": role_data.get("resonanceLevel", 0),
      "char_skill_level": [s.get("level", 1) for s in role_data.get("skillList", [])],
      "weapon_id": weapon_id,
      "weapon_level": role_data.get("weapon", {}).get("level", 1),
      "weapon_promote_level": role_data.get("weapon", {}).get("promoteLevel", 0),
      "weapon_reson_level": role_data.get("weapon", {}).get("resonanceLevel", 1),
      "echo_list": role_data.get("echoList", []),
      "sonata_list": role_data.get("sonataList", []),
      "buff_list": [],  # Buff 列表
      "enemy_id": "default",  # 默认敌人
      "enemy_level": 90,
      "enemy_promote_level": 6,
      "enemy_resist": {},
    }

    # 4. 执行计算
    try:
      damage_calc = Damage(damage_input, char_asc_data, weapon_asc_data)

      # 注册并执行角色、武器、声骸的 buff
      char_damage_func = get_char_damage_func(char_id)
      if char_damage_func:
        char_damage_func(damage_calc)

      weapon_damage_func = get_weapon_damage_func(weapon_id)
      if weapon_damage_func:
        weapon_damage_func(damage_calc)

      for echo in damage_input["echo_list"]:
        echo_id = str(echo.get("id", 0))
        echo_damage_func = get_echo_damage_func(echo_id)
        if echo_damage_func:
          echo_damage_func(damage_calc)

      # 最终计算
      calculated_ctx = damage_calc.calc()
      return calculated_ctx

    except Exception as e:
      return {"error": f"伤害计算出错: {e}"}

  async def get_character_panel_data(self, cookie: str, uid: str, role_id: int) -> Optional[Dict[str, Any]]:
    """
    获取角色面板所需的全部处理后数据
    (这是 char_info_utils.py 中 get_char_info_data 的重构版本)
    """
    cache_key = f"panel_data_{uid}_{role_id}"
    cached = await get_cache(cache_key)
    if cached:
      return json.loads(cached)

    # 1. 从 GameService 获取原始角色信息
    role_list_data = await self.game_service.get_role_info(cookie, uid)
    if not role_list_data or "roleList" not in role_list_data:
      return None  # 获取失败

    # 2. 查找目标角色
    target_role_data = None
    for role in role_list_data.get("roleList", []):
      if role.get("id") == role_id:
        target_role_data = role
        break

    if not target_role_data:
      return None  # 没找到该角色

    char_id_str = str(role_id)

    # 3. 格式化基础属性
    formatted_props = self._format_prop_data(target_role_data.get("attribute", []))
    target_role_data["formattedAttribute"] = formatted_props

    # 4. 计算声骸得分
    processed_echos, total_score = self._calc_echo_score(
        char_id_str,
        target_role_data.get("echoList", [])
    )
    target_role_data["echoList"] = processed_echos
    target_role_data["totalEchoScore"] = total_score

    # 5. 获取角色推荐词条
    target_role_data["recommendAttrs"] = get_char_score_pers(char_id_str)

    # 6. (关键) 运行伤害计算框架，获取详细属性
    # refresh_data = await self._refresh_char_detail(char_id_str, target_role_data)
    # target_role_data["refreshDetail"] = refresh_data

    # TODO: 伤害计算框架(refresh_data)暂未完全适配

    # 7. 缓存结果 (10分钟)
    await set_cache(cache_key, json.dumps(target_role_data), 600)

    return target_role_data

  # --- 新增方法 ---
  async def get_character_list_data(self, cookie: str, uid: str) -> Optional[Dict[str, Any]]:
    """
    获取角色列表所需的全部处理后数据
    (迁移自 wutheringwaves_charlist)
    """
    cache_key = f"char_list_data_{uid}"
    cached = await get_cache(cache_key)
    if cached:
      return json.loads(cached)

    # 1. 从 GameService 获取原始角色信息
    role_list_data = await self.game_service.get_role_info(cookie, uid)
    if not role_list_data or "roleList" not in role_list_data:
      return None  # 获取失败

    processed_roles = []
    total_account_score = 0.0

    # 2. 遍历所有角色，为他们计算声骸得分
    for role in role_list_data.get("roleList", []):
      char_id_str = str(role.get("id"))

      processed_echos, total_score = self._calc_echo_score(
          char_id_str,
          role.get("echoList", [])
      )
      role["echoList"] = processed_echos  # 替换为带分数的数据
      role["totalEchoScore"] = total_score
      total_account_score += total_score
      processed_roles.append(role)

    # 3. 替换回原数据
    role_list_data["roleList"] = processed_roles
    role_list_data["totalAccountScore"] = total_account_score

    # 4. 缓存结果 (10分钟)
    await set_cache(cache_key, json.dumps(role_list_data), 600)

    return role_list_data
  # --- 新增方法结束 ---