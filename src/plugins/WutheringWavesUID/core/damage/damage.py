# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/damage.py
from typing import Any, Dict

# 适配修改：
from ..utils.expression_evaluator import ExpressionCtx, ExpressionEvaluator
from ..ascension.model import CharAscensionData, WeaponAscensionData
# --- 修复：移除 PlayerInfo ---
# from ...models import PlayerInfo # 错误：此模型已不存在
# --- 修复结束 ---
from ..utils.util import sync_dict

from .abstract import DamageAbstract
from .constants import ECHO_MAIN_STAT


class Damage(DamageAbstract):
    def __init__(
            self,
            data: Dict[str, Any],
            char_data: CharAscensionData,
            weapon_data: WeaponAscensionData,
            # --- 修复：移除 PlayerInfo ---
            player_info: Any = None,  # 原为 player_info: PlayerInfo = None
            # --- 修复结束 ---
    ) -> None:
        # --- 修复：移除 PlayerInfo 逻辑 ---
        # if player_info:
        #     sync_dict(player_info.dict(), data)
        # --- 修复结束 ---
        super().__init__(data)
        self.char_data = char_data
        self.weapon_data = weapon_data
        self.evaluator = ExpressionEvaluator()

    def apply_char_ascension(self):
        ascensions = self.char_data["ascensions"]
        levels = self.char_data["levels"]
        promote_level = self.char_promote_level
        level = self.char_level

        ascension = ascensions[promote_level]
        level_data = levels[promote_level][level - 1]

        base_hp = level_data[0]
        base_atk = level_data[1]
        base_def = level_data[2]
        crit_rate = level_data[3]
        crit_dmg = level_data[4]

        extra_val: Dict[str, float] = {}
        for i in range(promote_level + 1):
            for k, v in ascensions[i]["extra_val"].items():
                extra_val[k] = extra_val.get(k, 0) + v

        self.ctx["角色基础生命"] = base_hp
        self.ctx["角色基础攻击"] = base_atk
        self.ctx["角色基础防御"] = base_def
        self.ctx["角色暴击率"] = crit_rate
        self.ctx["角色暴击伤害"] = crit_dmg

        for k, v in extra_val.items():
            self.ctx[f"角色{k}"] = v

    def apply_char_chain(self):
        pass

    def apply_char_skill(self):
        pass

    def apply_weapon_ascension(self):
        # 修复：检查武器数据是否存在
        if not self.weapon_data or not self.weapon_data.get("ascensions"):
            self.ctx["武器基础攻击"] = 0
            return  # 没有武器数据 (e.g., weapon_id="0")

        ascensions = self.weapon_data["ascensions"]
        levels = self.weapon_data["levels"]
        promote_level = self.weapon_promote_level
        level = self.weapon_level

        # 修复：防止索引越界
        if promote_level >= len(ascensions):
            promote_level = len(ascensions) - 1
        if level > ascensions[promote_level]["max_level"]:
            level = ascensions[promote_level]["max_level"]
        if level <= 0:
            level = 1

        ascension = ascensions[promote_level]
        level_data = levels[promote_level][level - 1]

        base_atk = level_data[0]
        extra_val = level_data[1]
        extra_key = ascension["extra_val"]["key"]

        self.ctx["武器基础攻击"] = base_atk
        self.ctx[f"武器{extra_key}"] = extra_val

    def apply_weapon_skill(self):
        pass

    def apply_echo_main_stat(self):
        for echo in self.echo_list:
            cost = echo["cost"]
            level = echo["level"]
            main_stat = echo["mainEntry"]  # 适配：已在 service 中处理
            main_key = main_stat["name"]  # 适配：使用 "name"
            main_val = main_stat["value"]  # 适配：使用 "value"

            self.ctx[f"声骸{main_key}"] = (
                    self.ctx.get(f"声骸{main_key}", 0) + main_val
            )

    def apply_echo_sub_stat(self):
        for echo in self.echo_list:
            sub_stats = echo["subEntry"]  # 适配：已在 service 中处理
            for sub_stat in sub_stats:
                sub_key = sub_stat["key"]  # 适配：使用 "key"
                sub_val = sub_stat["value"]  # 适配：使用 "value"
                self.ctx[f"声骸{sub_key}"] = (
                        self.ctx.get(f"声骸{sub_key}", 0) + sub_val
                )

    def apply_echo_skill(self):
        pass

    def apply_sonata_effect(self):
        pass

    def apply_buff(self):
        pass

    def apply_enemy(self):
        pass

    def _init_ctx(self):
        keys = [
            "基础生命",
            "基础攻击",
            "基础防御",
            "生命",
            "生命值",
            "攻击",
            "攻击力",
            "防御",
            "防御力",
            "暴击率",
            "暴击伤害",
            "治疗效果加成",
            "共鸣效率",
            "冷却缩减",
            "普攻伤害加成",
            "重击伤害加成",
            "共鸣技能伤害加成",
            "共鸣解放伤害加成",
            "变奏技能伤害加成",
            "延奏技能伤害加成",
            "冷凝伤害加成",
            "热熔伤害加成",
            "导电伤害加成",
            "气动伤害加成",
            "衍射伤害加成",
            "湮灭伤害加成",
            "物理伤害加成",
            "冷凝伤害抗性",
            "热熔伤害抗性",
            "导电伤害抗性",
            "气动伤害抗性",
            "衍射伤害抗性",
            "湮灭伤害抗性",
            "物理伤害抗性",
            "伤害加成",
            "承疗效果加成",
            "基础伤害",
            "基础伤害倍率",
            "伤害倍率",
            "基础额外伤害",
            "额外伤害",
            "额外伤害倍率",
            "技能伤害",
            "技能伤害倍率",
            "普攻伤害",
            "普攻伤害倍率",
            "重击伤害",
            "重击伤害倍率",
            "共鸣技能伤害",
            "共鸣技能伤害倍率",
            "共鸣解放伤害",
            "共鸣解放伤害倍率",
            "变奏技能伤害",
            "变奏技能伤害倍率",
            "延奏技能伤害",
            "延奏技能伤害倍率",
        ]
        for key in keys:
            if f"角色{key}" not in self.ctx:
                self.ctx[f"角色{key}"] = 0
            if f"武器{key}" not in self.ctx:
                self.ctx[f"武器{key}"] = 0
            if f"声骸{key}" not in self.ctx:
                self.ctx[f"声骸{key}"] = 0
            if f"套装{key}" not in self.ctx:
                self.ctx[f"套装{key}"] = 0
            if f"增益{key}" not in self.ctx:
                self.ctx[f"增益{key}"] = 0

            self.ctx[key] = (
                    self.ctx.get(f"角色{key}", 0)
                    + self.ctx.get(f"武器{key}", 0)
                    + self.ctx.get(f"声骸{key}", 0)
                    + self.ctx.get(f"套装{key}", 0)
                    + self.ctx.get(f"增益{key}", 0)
            )

        # total
        self.ctx["生命值"] = (
                self.ctx["角色基础生命"] * (1 + self.ctx["生命"]) + self.ctx["生命值"]
        )
        self.ctx["攻击力"] = (
                (self.ctx["角色基础攻击"] + self.ctx["武器基础攻击"])
                * (1 + self.ctx["攻击"])
                + self.ctx["攻击力"]
        )
        self.ctx["防御力"] = (
                self.ctx["角色基础防御"] * (1 + self.ctx["防御"]) + self.ctx["防御力"]
        )

    def calc(self) -> Dict[str, Any]:
        self.apply_char_ascension()
        self.apply_char_chain()
        self.apply_char_skill()
        self.apply_weapon_ascension()
        self.apply_weapon_skill()
        self.apply_echo_main_stat()
        self.apply_echo_sub_stat()
        self.apply_echo_skill()
        self.apply_sonata_effect()
        self.apply_buff()
        self.apply_enemy()
        self._init_ctx()

        return self.ctx

    def eval(self, expr: str) -> float:
        return self.evaluator.eval(expr, ExpressionCtx(self.ctx))