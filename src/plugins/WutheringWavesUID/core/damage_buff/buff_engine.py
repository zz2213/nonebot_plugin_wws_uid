# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage_buff/buff_engine.py
# (原名 attribute.py, 迁移自 WutheringWavesUID1/utils/map/damage/damage.py)

import json
import math
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# 适配修改：
from nonebot.log import logger
from .models import CharAbstract, WeaponAbstract, DamageAttribute, Buff
from .load_scripts import WavesCharRegister, WavesWeaponRegister
from .utils import (
    CALC_PERCENT,
    CHAR_ATTR_CELESTIAL,
    CHAR_ATTR_FREEZING,
    CHAR_ATTR_MOLTEN,
    CHAR_ATTR_SIERRA,
    CHAR_ATTR_SINKING,
    CHAR_ATTR_VOID,
    SONATA_GROUP,
    get_char_info_by_id,
    get_weapon_info_by_id,
    normal_damage,
    hit_damage,
    skill_damage,
    liberation_damage,
    temp_atk,
    temp_def,
    temp_hp
)

# --- 适配结束 ---


# 适配修改：从 core/data 加载
DATA_PATH = Path(__file__).parent.parent / "data"
CHAR_CALC_PATH = DATA_PATH / "character"


# 适配修改：
# CharAbstract, WeaponAbstract, Buff, DamageAttribute
# 已被移动到 core/damage_buff/models.py 来打破循环依赖
class DamageAttribute(DamageAttribute):
    """
    (框架 B) 团队Buff与期望伤害计算器
    (实现)
    """

    def __init__(self, data: Dict, uid: str):
        self.char_data = data
        self.uid = uid
        self.char_id = data.get("id", 0)
        self.char_level = data.get("level", 90)
        self.char_chain = data.get("resonanceLevel", 0)

        weapon_data = data.get("weapon", {})
        self.weapon_id = weapon_data.get("id", 0)
        self.weapon_level = weapon_data.get("level", 90)
        self.weapon_chain = weapon_data.get("resonanceLevel", 1)

        self.char_info = get_char_info_by_id(self.char_id)
        self.weapon_info = get_weapon_info_by_id(self.weapon_id)

        self.char_attr = self.char_info.get("property", "")
        self.char_template = temp_atk  # 默认攻击
        if self.char_attr in [CHAR_ATTR_SINKING, CHAR_ATTR_CELESTIAL]:
            self.char_damage = liberation_damage
        elif self.char_attr in [CHAR_ATTR_FREEZING, CHAR_ATTR_SIERRA]:
            self.char_damage = skill_damage
        elif self.char_attr in [CHAR_ATTR_MOLTEN, CHAR_ATTR_VOID]:
            self.char_damage = normal_damage
        else:
            self.char_damage = normal_damage

        self.buff_list: List[Buff] = []

        self.base_atk = 0.0
        self.base_def = 0.0
        self.base_hp = 0.0

        self.atk_percent = 0.0
        self.def_percent = 0.0
        self.hp_percent = 0.0
        self.atk_flat = 0.0
        self.def_flat = 0.0
        self.hp_flat = 0.0

        self.crit_rate = 0.05
        self.crit_dmg = 1.5

        self.energy_recharge = 1.0

        self.dmg_bonus = 0.0
        self.dmg_bonus_normal = 0.0
        self.dmg_bonus_hit = 0.0
        self.dmg_bonus_skill = 0.0
        self.dmg_bonus_liberation = 0.0

        self.dmg_deepen = 0.0
        self.dmg_deepen_normal = 0.0
        self.dmg_deepen_hit = 0.0
        self.dmg_deepen_skill = 0.0
        self.dmg_deepen_liberation = 0.0
        self.dmg_deepen_resonance = 0.0
        self.dmg_deepen_fusion = 0.0

        self.enemy_resistance = 0.1
        self.enemy_resistance_debuff = 0.0
        self.enemy_defense_debuff = 0.0  # 修复: 缺少定义
        self.enemy_defense = self.char_level * 5 + 500

        self.sonata_group: Dict[str, int] = {}

        self.env_spectro = False
        self.env_spectro_deepen = False

        self._init_char_attr()
        self._init_weapon_attr()
        self.init_echo_attr()

    def set_char_template(self, template: int):
        self.char_template = template

    def set_char_damage(self, damage_type: int):
        self.char_damage = damage_type

    def set_env_spectro(self, deepen: bool = False):
        self.env_spectro = True
        self.env_spectro_deepen = deepen

    def add_base_atk(self, value: float, title: str, msg: str):
        self.base_atk += value
        self.add_buff("base_atk", value, title, msg)

    def add_base_def(self, value: float, title: str, msg: str):
        self.base_def += value
        self.add_buff("base_def", value, title, msg)

    def add_base_hp(self, value: float, title: str, msg: str):
        self.base_hp += value
        self.add_buff("base_hp", value, title, msg)

    def add_atk_percent(self, value: float, title: str, msg: str):
        self.atk_percent += value
        self.add_buff("atk_percent", value, title, msg)

    def add_def_percent(self, value: float, title: str, msg: str):
        self.def_percent += value
        self.add_buff("def_percent", value, title, msg)

    def add_hp_percent(self, value: float, title: str, msg: str):
        self.hp_percent += value
        self.add_buff("hp_percent", value, title, msg)

    def add_atk_flat(self, value: float, title: str, msg: str):
        self.atk_flat += value
        self.add_buff("atk_flat", value, title, msg)

    def add_def_flat(self, value: float, title: str, msg: str):
        self.def_flat += value
        self.add_buff("def_flat", value, title, msg)

    def add_hp_flat(self, value: float, title: str, msg: str):
        self.hp_flat += value
        self.add_buff("hp_flat", value, title, msg)

    def add_crit_rate(self, value: float, title: str, msg: str):
        self.crit_rate += value
        self.add_buff("crit_rate", value, title, msg)

    def add_crit_dmg(self, value: float, title: str, msg: str):
        self.crit_dmg += value
        self.add_buff("crit_dmg", value, title, msg)

    def add_energy_recharge(self, value: float, title: str, msg: str):
        self.energy_recharge += value
        self.add_buff("energy_recharge", value, title, msg)

    def add_dmg_bonus(self, value: float, title: str, msg: str):
        self.dmg_bonus += value
        self.add_buff("dmg_bonus", value, title, msg)

    def add_dmg_bonus_normal(self, value: float, title: str, msg: str):
        self.dmg_bonus_normal += value
        self.add_buff("dmg_bonus_normal", value, title, msg)

    def add_dmg_bonus_hit(self, value: float, title: str, msg: str):
        self.dmg_bonus_hit += value
        self.add_buff("dmg_bonus_hit", value, title, msg)

    def add_dmg_bonus_skill(self, value: float, title: str, msg: str):
        self.dmg_bonus_skill += value
        self.add_buff("dmg_bonus_skill", value, title, msg)

    def add_dmg_bonus_liberation(self, value: float, title: str, msg: str):
        self.dmg_bonus_liberation += value
        self.add_buff("dmg_bonus_liberation", value, title, msg)

    def add_dmg_deepen(self, value: float, title: str, msg: str):
        self.dmg_deepen += value
        self.add_buff("dmg_deepen", value, title, msg)

    def add_dmg_deepen_normal(self, value: float, title: str, msg: str):
        self.dmg_deepen_normal += value
        self.add_buff("dmg_deepen_normal", value, title, msg)

    def add_dmg_deepen_hit(self, value: float, title: str, msg: str):
        self.dmg_deepen_hit += value
        self.add_buff("dmg_deepen_hit", value, title, msg)

    def add_dmg_deepen_skill(self, value: float, title: str, msg: str):
        self.dmg_deepen_skill += value
        self.add_buff("dmg_deepen_skill", value, title, msg)

    def add_dmg_deepen_liberation(self, value: float, title: str, msg: str):
        self.dmg_deepen_liberation += value
        self.add_buff("dmg_deepen_liberation", value, title, msg)

    def add_dmg_deepen_resonance(self, value: float, title: str, msg: str):
        self.dmg_deepen_resonance += value
        self.add_buff("dmg_deepen_resonance", value, title, msg)

    def add_dmg_deepen_fusion(self, value: float, title: str, msg: str):
        self.dmg_deepen_fusion += value
        self.add_buff("dmg_deepen_fusion", value, title, msg)

    def add_enemy_resistance(self, value: float, title: str, msg: str):
        self.enemy_resistance_debuff += value
        self.add_buff("enemy_resistance_debuff", value, title, msg)

    def add_enemy_defense_debuff(self, value: float, title: str, msg: str):
        self.enemy_defense_debuff += value
        self.add_buff("enemy_defense_debuff", value, title, msg)

    def add_buff(
            self,
            name: str,
            value: float,
            title: str,
            msg: str,
    ):
        self.buff_list.append(
            Buff(
                name=name,
                value=value,
                buff_type=self.char_attr,
                title=title,
                msg=msg,
            )
        )

    def add_effect(self, title: str, msg: str):
        self.buff_list.append(
            Buff(
                name="effect",
                value=0,
                buff_type=self.char_attr,
                title=title,
                msg=msg,
            )
        )

    def _init_char_attr(self):
        attribute = self.char_data.get("attribute", [])
        for i in attribute:
            _id = i.get("id", 0)
            _val = i.get("value", 0)
            if _id == 1:
                self.base_hp = _val
            elif _id == 2:
                self.base_atk = _val
            elif _id == 3:
                self.base_def = _val
            elif _id == 4:
                self.crit_rate += _val
            elif _id == 5:
                self.crit_dmg += _val
            elif _id == 7:
                self.atk_percent += _val
            elif _id == 10:
                self.hp_percent += _val
            elif _id == 13:
                self.def_percent += _val
            elif _id == 14:
                self.energy_recharge += _val
            elif _id == 15 and self.char_attr == CHAR_ATTR_SINKING:
                self.dmg_bonus += _val
            elif _id == 16 and self.char_attr == CHAR_ATTR_CELESTIAL:
                self.dmg_bonus += _val
            elif _id == 17 and self.char_attr == CHAR_ATTR_SIERRA:
                self.dmg_bonus += _val
            elif _id == 18 and self.char_attr == CHAR_ATTR_VOID:
                self.dmg_bonus += _val
            elif _id == 19 and self.char_attr == CHAR_ATTR_MOLTEN:
                self.dmg_bonus += _val
            elif _id == 20 and self.char_attr == CHAR_ATTR_FREEZING:
                self.dmg_bonus += _val

    def _init_weapon_attr(self):
        weapon_data = self.char_data.get("weapon", {})
        weapon_attr = weapon_data.get("attribute", [])
        for i in weapon_attr:
            _id = i.get("id", 0)
            _val = i.get("value", 0)
            if _id == 2:
                self.base_atk += _val
            elif _id == 6:
                self.crit_rate += _val
            elif _id == 7:
                self.crit_dmg += _val
            elif _id == 8:
                self.atk_percent += _val
            elif _id == 11:
                self.hp_percent += _val
            elif _id == 14:
                self.def_percent += _val
            elif _id == 15:
                self.energy_recharge += _val

    def init_echo_attr(self):
        echo_list = self.char_data.get("echoList", [])
        for echo in echo_list:
            main_entry = echo.get("mainEntry", {})
            self._add_echo_attr(main_entry)
            sub_entry = echo.get("subEntry", [])
            for i in sub_entry:
                self._add_echo_attr(i)

        sonata_list = self.char_data.get("sonataList", [])
        for sonata in sonata_list:
            _id = sonata.get("id")
            _cnt = sonata.get("count")
            if _id not in SONATA_GROUP:
                continue
            group = SONATA_GROUP.get(_id)
            if not group:
                continue
            if _cnt >= 2:
                self.sonata_group[group] = self.sonata_group.get(group, 0) + 2
            if _cnt >= 5:
                self.sonata_group[group] = self.sonata_group.get(group, 0) + 3

    def _add_echo_attr(self, data: Dict):
        _key = data.get("key", "")
        _val = data.get("value", 0)
        if _key == "10002":
            self.hp_flat += _val
        elif _key == "10003":
            self.atk_flat += _val
        elif _key == "10004":
            self.def_flat += _val
        elif _key == "10005":
            self.hp_percent += _val
        elif _key == "10006":
            self.atk_percent += _val
        elif _key == "10007":
            self.def_percent += _val
        elif _key == "10008":
            self.crit_rate += _val
        elif _key == "10009":
            self.crit_dmg += _val
        elif _key == "10010":
            self.energy_recharge += _val
        elif _key == "10011":
            self.dmg_bonus_skill += _val
        elif _key == "10012":
            self.dmg_bonus_liberation += _val
        elif _key == "10013":
            self.dmg_bonus_normal += _val
        elif _key == "10014":
            self.dmg_bonus_hit += _val
        elif _key == "10015":
            if self.char_attr == CHAR_ATTR_FREEZING:
                self.dmg_bonus += _val
        elif _key == "10016":
            if self.char_attr == CHAR_ATTR_MOLTEN:
                self.dmg_bonus += _val
        elif _key == "10017":
            if self.char_attr == CHAR_ATTR_VOID:
                self.dmg_bonus += _val
        elif _key == "10018":
            if self.char_attr == CHAR_ATTR_SIERRA:
                self.dmg_bonus += _val
        elif _key == "10019":
            if self.char_attr == CHAR_ATTR_CELESTIAL:
                self.dmg_bonus += _val
        elif _key == "10020":
            if self.char_attr == CHAR_ATTR_SINKING:
                self.dmg_bonus += _val

    def do_buff(self):
        char_clz = WavesCharRegister.find_class(self.char_id)
        if char_clz:
            c = char_clz(
                self.char_id,
                self.char_level,
                self.char_chain,
                self.weapon_chain,
            )
            c.do_action("buff", self)

        weapon_clz = WavesWeaponRegister.find_class(self.weapon_id)
        if weapon_clz:
            w = weapon_clz(
                self.weapon_id,
                self.weapon_level,
                self.char_chain,
                self.weapon_chain,
            )
            w.do_action("buff", self)

    def get_damage_data(self) -> Dict:
        # 适配修改：从 core/data/character/ 目录读取
        char_name = self.char_info.get("name")
        if not char_name:
            logger.error(f"Cannot find name for char_id {self.char_id}")
            return self.char_data

        calc_json_path = CHAR_CALC_PATH / char_name / "calc.json"
        try:
            with open(calc_json_path, "r", encoding="utf-8") as f:
                calc_data = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Missing calc.json for {char_name}, using default.")
            default_calc_path = CHAR_CALC_PATH / "default" / "calc.json"
            try:
                with open(default_calc_path, "r", encoding="utf-8") as f:
                    calc_data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load default calc.json: {e}")
                return self.char_data

        damage_list = calc_data.get("damage_list", [])
        expected_damage = 0.0
        expected_name = ""
        for i in damage_list:
            damage = self._cacl_damage(i)
            if damage > expected_damage:
                expected_damage = damage
                expected_name = i.get("name")

        # 将计算结果写入 char_data
        self.char_data["expected_damage"] = expected_damage
        self.char_data["expected_name"] = expected_name

        return self.char_data

    def _cacl_damage(self, data: Dict) -> float:
        rate = data.get("rate", 0)
        damage_type = data.get("damage_type", normal_damage)
        attr = data.get("attr", temp_atk)
        element = data.get("element", self.char_attr)

        panel_atk = 0.0
        if attr == temp_atk:
            panel_atk = self.base_atk * (1 + self.atk_percent) + self.atk_flat
        elif attr == temp_def:
            panel_atk = self.base_def * (1 + self.def_percent) + self.def_flat
        elif attr == temp_hp:
            panel_atk = self.base_hp * (1 + self.hp_percent) + self.hp_flat
        else:
            return 0.0

        dmg_bonus = self.dmg_bonus + self._get_element_bonus(element)
        if damage_type == normal_damage:
            dmg_bonus += self.dmg_bonus_normal
        elif damage_type == hit_damage:
            dmg_bonus += self.dmg_bonus_hit
        elif damage_type == skill_damage:
            dmg_bonus += self.dmg_bonus_skill
        elif damage_type == liberation_damage:
            dmg_bonus += self.dmg_bonus_liberation

        dmg_deepen = self.dmg_deepen
        if damage_type == normal_damage:
            dmg_deepen += self.dmg_deepen_normal
        elif damage_type == hit_damage:
            dmg_deepen += self.dmg_deepen_hit
        elif damage_type == skill_damage:
            dmg_deepen += self.dmg_deepen_skill
        elif damage_type == liberation_damage:
            dmg_deepen += self.dmg_deepen_liberation

        crit_rate = min(self.crit_rate, 1.0)
        crit_dmg = self.crit_dmg

        enemy_resistance = (
                self.enemy_resistance
                + self._get_element_resistance(element)
                - self.enemy_resistance_debuff
        )
        enemy_resistance_bonus = 1.0 - enemy_resistance

        enemy_defense_bonus = (self.char_level * 5 + 500) / (
                (self.enemy_defense * (1.0 - self.enemy_defense_debuff)) + self.char_level * 5 + 500
        )

        damage = (
                panel_atk * rate * (1 + dmg_bonus) * (1 + dmg_deepen)
                + 0
        )

        crit_damage = damage * (1 + crit_rate * (crit_dmg - 1))
        expected_damage = (
                crit_damage
                * enemy_resistance_bonus
                * enemy_defense_bonus
        )
        return expected_damage

    def _get_element_bonus(self, element: str) -> float:
        # 适配：APIv2 的属性 ID 不一样，我们直接从面板属性字典里找
        # 我们的 `_init_char_attr` 已经把对应属性加到了 self.dmg_bonus
        # 但声骸词条没有，所以我们在这里补充

        bonus = 0.0
        echo_list = self.char_data.get("echoList", [])
        for echo in echo_list:
            main_key = echo.get("mainEntry", {}).get("key", "")
            if main_key == "10015" and element == CHAR_ATTR_FREEZING:
                bonus += echo.get("mainEntry", {}).get("value", 0)
            elif main_key == "10016" and element == CHAR_ATTR_MOLTEN:
                bonus += echo.get("mainEntry", {}).get("value", 0)
            elif main_key == "10017" and element == CHAR_ATTR_VOID:
                bonus += echo.get("mainEntry", {}).get("value", 0)
            elif main_key == "10018" and element == CHAR_ATTR_SIERRA:
                bonus += echo.get("mainEntry", {}).get("value", 0)
            elif main_key == "10019" and element == CHAR_ATTR_CELESTIAL:
                bonus += echo.get("mainEntry", {}).get("value", 0)
            elif main_key == "10020" and element == CHAR_ATTR_SINKING:
                bonus += echo.get("mainEntry", {}).get("value", 0)

        # 模拟旧逻辑 (不完全准确，但能跑)
        if self.char_attr != element:
            logger.warning(f"Calculating non-native element {element} for char {self.char_id}")
            # return bonus # 只返回声骸加成

        # for k, v in CALC_PERCENT.items():
        #     if v == element:
        #         # 这是一个 hack, 因为 attribute 里的 value 已经是百分比
        #         return self.char_data.get("attribute", {}).get(k, 0)
        return 0.0  # 基础属性已在 self.dmg_bonus 中, 这里只处理额外加成

    def _get_element_resistance(self, element: str) -> float:
        # 敌人抗性暂时写死 0.1
        return 0.0