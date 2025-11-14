# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage_buff/models.py
# (新文件，用于打破 buff_engine 和 load_scripts 之间的循环依赖)

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from nonebot.log import logger


# --- 抽象类 ---

class CharAbstract:
    """(框架 B) 角色抽象基类"""
    id = 0
    name = "unknown"
    starLevel = 0

    def __init__(
            self,
            char_id: int,
            level: int,
            chain: int,
            resonLevel: int,
    ) -> None:
        self.char_id = char_id
        self.level = level
        self.chain = chain
        self.resonLevel = resonLevel

    def do_action(
            self,
            action: str,
            attr: "DamageAttribute",
            isGroup: bool = False,
            *args: Any,
            **kwds: Any,
    ):
        method = getattr(self, f"_do_{action}", None)
        if callable(method):
            method(attr, self.chain, self.resonLevel, isGroup, *args, **kwds)
        else:
            logger.info(f"[Framework B] 角色[{self.name}]未实现动作[{action}]")


class WeaponAbstract(CharAbstract):
    """(框架 B) 武器抽象基类"""
    pass


# --- Buff 模型 ---

class Buff:
    def __init__(
            self,
            name: str,
            value: float,
            buff_type: str,
            title: str,
            msg: str,
    ):
        self.name = name
        self.value = value
        self.buff_type = buff_type
        self.title = title
        self.msg = msg


# --- 属性计算器模型 ---

class DamageAttribute:
    """(框架 B) 团队Buff与期望伤害计算器"""

    # 这只是一个模型定义，实现在 buff_engine.py 中
    # 这里定义是为了让 load_scripts.py 和 buff_engine.py 都能导入

    char_data: Dict
    uid: str
    char_id: int
    char_level: int
    char_chain: int
    weapon_id: int
    weapon_level: int
    weapon_chain: int
    char_info: Dict
    weapon_info: Dict
    char_attr: str
    char_template: int
    char_damage: int
    buff_list: List[Buff]
    base_atk: float
    base_def: float
    base_hp: float
    atk_percent: float
    def_percent: float
    hp_percent: float
    atk_flat: float
    def_flat: float
    hp_flat: float
    crit_rate: float
    crit_dmg: float
    energy_recharge: float
    dmg_bonus: float
    dmg_bonus_normal: float
    dmg_bonus_hit: float
    dmg_bonus_skill: float
    dmg_bonus_liberation: float
    dmg_deepen: float
    dmg_deepen_normal: float
    dmg_deepen_hit: float
    dmg_deepen_skill: float
    dmg_deepen_liberation: float
    dmg_deepen_resonance: float
    dmg_deepen_fusion: float
    enemy_resistance: float
    enemy_resistance_debuff: float
    enemy_defense: float
    sonata_group: Dict[str, int]
    env_spectro: bool
    env_spectro_deepen: bool

    def __init__(self, data: Dict, uid: str):
        raise NotImplementedError("This is an abstract model.")

    def add_atk_percent(self, value: float, title: str, msg: str): ...

    def add_dmg_bonus(self, value: float, title: str, msg: str): ...

    def add_dmg_deepen(self, value: float, title: str, msg: str): ...

    def add_enemy_resistance(self, value: float, title: str, msg: str): ...
    # ... (其他 add_... 方法)