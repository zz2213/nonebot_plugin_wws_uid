# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/ascension/template.py
from typing import Dict, Generic, List, TypeVar

from .model import AscensionBase

T = TypeVar("T", bound=AscensionBase)


class AscensionTemplate(Generic[T]):
    def __init__(self, data: List[T], levels: List[List[float]]) -> None:
        self.data = data
        self.levels = levels

    def get_ascension(self, promote_level: int) -> T:
        return self.data[promote_level]

    def get_level(self, promote_level: int, level: int) -> List[float]:
        return self.levels[promote_level][level - 1]

    def get_max_level(self, promote_level: int) -> int:
        return self.data[promote_level]["max_level"]

    def get_promote_cost(self, promote_level: int) -> Dict[str, int]:
        return self.data[promote_level]["promote_cost"]

    def get_base_val(self, promote_level: int) -> float:
        return self.data[promote_level]["base_val"]

    def get_inc_val(self, promote_level: int) -> float:
        return self.data[promote_level]["inc_val"]

    def get_all_levels(self, promote_level: int, level: int) -> List[float]:
        levels = []
        for i in range(promote_level + 1):
            if i < promote_level:
                levels.extend(self.levels[i])
            else:
                levels.extend(self.levels[i][:level])
        return levels