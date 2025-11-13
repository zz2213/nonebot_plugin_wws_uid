# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/abstract.py
from typing import Any, Dict, List, Union


class DamageAbstract:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        self.char_id: str = data["char_id"]
        self.char_level: int = data["char_level"]
        self.char_promote_level: int = data["char_promote_level"]
        self.char_chain: int = data["char_chain"]
        self.char_skill_level: List[int] = data["char_skill_level"]
        self.weapon_id: str = data["weapon_id"]
        self.weapon_level: int = data["weapon_level"]
        self.weapon_promote_level: int = data["weapon_promote_level"]
        self.weapon_reson_level: int = data["weapon_reson_level"]
        self.echo_list: List[Dict[str, Any]] = data["echo_list"]
        self.sonata_list: List[Dict[str, Any]] = data["sonata_list"]
        self.buff_list: List[Dict[str, Any]] = data["buff_list"]
        self.enemy_id: str = data["enemy_id"]
        self.enemy_level: int = data["enemy_level"]
        self.enemy_promote_level: int = data["enemy_promote_level"]
        self.enemy_resist: Dict[str, float] = data["enemy_resist"]

        self.ctx: Dict[str, Any] = {}

    def apply_char_ascension(self):
        """角色突破"""
        raise NotImplementedError

    def apply_char_chain(self):
        """角色共鸣链"""
        raise NotImplementedError

    def apply_char_skill(self):
        """角色技能"""
        raise NotImplementedError

    def apply_weapon_ascension(self):
        """武器突破"""
        raise NotImplementedError

    def apply_weapon_skill(self):
        """武器技能"""
        raise NotImplementedError

    def apply_echo_main_stat(self):
        """声骸主词条"""
        raise NotImplementedError

    def apply_echo_sub_stat(self):
        """声骸副词条"""
        raise NotImplementedError

    def apply_echo_skill(self):
        """声骸技能"""
        raise NotImplementedError

    def apply_sonata_effect(self):
        """声骸套装效果"""
        raise NotImplementedError

    def apply_buff(self):
        """增益"""
        raise NotImplementedError

    def apply_enemy(self):
        """敌人"""
        raise NotImplementedError

    def calc(self) -> Dict[str, Any]:
        """计算"""
        raise NotImplementedError