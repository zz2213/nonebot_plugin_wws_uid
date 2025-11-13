# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/ascension/model.py
from typing import Dict, List, TypedDict


class AscensionBase(TypedDict):
    max_level: int
    promote_level: int
    promote_cost: Dict[str, int]
    base_val: float
    inc_val: float


class AscensionChar(AscensionBase):
    extra_val: Dict[str, float]


class AscensionWeapon(AscensionBase):
    pass


class AscensionEcho(TypedDict):
    max_level: int
    cost: int
    base_val: float
    inc_val: float


class AscensionSonata(TypedDict):
    active_num: int
    effect: str


class WeaponAscensionData(TypedDict):
    ascensions: List[AscensionWeapon]
    levels: List[List[float]]


class CharAscensionData(TypedDict):
    ascensions: List[AscensionChar]
    levels: List[List[float]]


class EchoAscensionData(TypedDict):
    ascensions: List[AscensionEcho]
    levels: List[List[float]]


class SonataAscensionData(TypedDict):
    ascensions: List[AscensionSonata]