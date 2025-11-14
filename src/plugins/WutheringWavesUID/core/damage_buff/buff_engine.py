# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage_buff/buff_engine.py

from typing import Any, Callable, Dict, List, Literal, Optional, TypedDict
from pydantic import BaseModel, Field
from pathlib import Path

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..data.damage.register import (
    WavesCharRegister, WavesWeaponRegister, WavesEchoRegister, WavesSonataRegister
)
from ..utils.image_helpers import get_attribute

# --- 导入完成 ---


# --- 资源路径定义 ---
# 适配修改：路径指向 core/data/
DATA_PATH = Path(__file__).parent.parent.parent / "core" / "data"


# --- 路径定义完成 ---


# --- Pydantic 模型 (来自 wutheringwaves_master) ---
class DamageResult(TypedDict):
    name: str
    val: float
    is_crit: bool


class DamageDetail(TypedDict):
    title: str
    msg: str


class DamageAttributeData(BaseModel):
    name: str = Field(default="Unknown", description="角色名称")
    uid: str = Field(default="", description="用户UID")
    level: int = Field(default=90, description="角色等级")
    chain: int = Field(default=0, description="角色共鸣链")
    # ... (其他字段)


# --- 核心类 (来自 wutheringwaves_master) ---

class DamageAttribute:
    def __init__(self, data: DamageAttributeData):
        self.data = data
        self.char_level = data.level
        self.char_chain = data.chain
        self.char_name = data.name

        # 初始化属性
        self.atk_base = data.atk_base
        self.atk_percent = data.atk_percent
        self.atk_flat = data.atk_flat
        self.crit_rate = data.crit_rate
        self.crit_dmg = data.crit_dmg
        self.dmg_bonus = data.dmg_bonus
        self.heal_bonus = data.heal_bonus
        self.energy = data.energy

        # 伤害加深
        self.dmg_deepen = 0.0
        # 额外伤害 (例如吟霖)
        self.extra_dmg = 0.0

        # 敌人属性
        self.enemy_level: int = 90
        self.enemy_resistance: float = 0.1
        self.enemy_resistance_debuff: float = 0.0

        # Buff 详情
        self.buff_list: List[DamageDetail] = []
        self.char_attr: str = data.char_attr  # e.g., "导电"

        # 环境
        self.env_spectro_deepen: bool = False  # 光噪效应

    # --- Buff 添加方法 ---
    def add_atk_percent(self, val: float, title: str, msg: str):
        self.atk_percent += val
        self.buff_list.append({"title": title, "msg": msg})

    def add_atk_flat(self, val: float, title: str, msg: str):
        self.atk_flat += val
        self.buff_list.append({"title": title, "msg": msg})

    def add_crit_rate(self, val: float, title: str = "", msg: str = ""):
        self.crit_rate += val
        if title: self.buff_list.append({"title": title, "msg": msg})

    def add_crit_dmg(self, val: float, title: str = "", msg: str = ""):
        self.crit_dmg += val
        if title: self.buff_list.append({"title": title, "msg": msg})

    def add_dmg_bonus(self, val: float, title: str = "", msg: str = ""):
        self.dmg_bonus += val
        if title: self.buff_list.append({"title": title, "msg": msg})

    def add_dmg_deepen(self, val: float, title: str, msg: str):
        self.dmg_deepen += val
        self.buff_list.append({"title": title, "msg": msg})

    def add_enemy_resistance(self, val: float, title: str, msg: str):
        self.enemy_resistance_debuff += val
        self.buff_list.append({"title": title, "msg": msg})

    def set_env_spectro(self):
        self.env_spectro_deepen = True

    def add_effect(self, title: str, msg: str):
        self.buff_list.append({"title": title, "msg": msg})

    # --- 最终计算 ---
    def get_atk(self) -> float:
        """计算总攻击力"""
        return self.atk_base * (1 + self.atk_percent) + self.atk_flat

    def get_enemy_resistance(self) -> float:
        """计算敌人最终抗性"""
        res = self.enemy_resistance - self.enemy_resistance_debuff
        return res

    def get_damage(
            self,
            rate: float,
            damage_type: str = "共鸣技能",
            is_crit: bool = False,
    ) -> DamageResult:
        """
        计算伤害
        :param rate: 倍率
        :param damage_type: 伤害类型 (e.g., "普攻", "共鸣技能")
        :param is_crit: 是否暴击
        """
        atk = self.get_atk()
        crit_val = self.crit_dmg if is_crit else 0.0

        # 伤害加成
        dmg_bonus = self.dmg_bonus

        # 敌人防御区
        def_reduce = (self.char_level * 5 + 500) / \
                     (self.enemy_level * 5 + 500 + (self.char_level * 5 + 500))

        # 敌人抗性区
        enemy_res = self.get_enemy_resistance()
        res_reduce = 1.0 - enemy_res

        # 伤害加深区
        deepen_reduce = 1.0 + self.dmg_deepen

        # 计算
        val = (atk * rate + self.extra_dmg) * \
              (1 + crit_val) * \
              (1 + dmg_bonus) * \
              def_reduce * \
              res_reduce * \
              deepen_reduce

        return {"name": damage_type, "val": val, "is_crit": is_crit}

    def get_damage_val(
            self,
            rate: float,
            damage_type: str = "共鸣技能",
            expected: bool = True,
    ) -> DamageResult:
        """计算期望伤害"""
        if not expected:
            return self.get_damage(rate, damage_type, is_crit=False)

        # 期望 = 爆伤 * 暴击率 + 不爆伤 * (1 - 暴击率)
        crit_rate = min(1.0, self.crit_rate)

        crit_dmg = self.get_damage(rate, damage_type, is_crit=True)["val"]
        non_crit_dmg = self.get_damage(rate, damage_type, is_crit=False)["val"]

        val = (crit_dmg * crit_rate) + (non_crit_dmg * (1 - crit_rate))

        return {"name": damage_type, "val": val, "is_crit": False}


class CharAbstract:
    """
    (Framework B) 角色 Buff 计算抽象类
    (迁移自 wutheringwaves_master)
    """
    id: int = 0
    name: str = "Unknown"
    starLevel: int = 4

    def __init__(
            self,
            char_id: int,
            level: int = 90,
            chain: int = 0,
            resonLevel: int = 1,
    ):
        self.char_id = char_id
        self.level = level
        self.chain = chain
        self.resonLevel = resonLevel  # 武器阶级

    def do_action(
            self,
            action: str,
            attr: DamageAttribute,
            isGroup: bool = True,
    ):
        method = getattr(self, f"_do_{action}", None)
        if callable(method):
            method(attr, self.chain, self.resonLevel, isGroup)