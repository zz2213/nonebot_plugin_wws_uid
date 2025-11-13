# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/register_weapon.py
from typing import Any, Callable, Dict

# 适配修改：从 from utils.map.damage.register import ...
from ..data.damage.register import (
    register_weapon as _register_weapon,
    get_weapon as _get_weapon,
)
from .abstract import DamageAbstract

PROCESSOR: Dict[str, Callable[[DamageAbstract], Dict[str, Any]]] = {}


def register_weapon(
    weapon_id: str,
) -> Callable[[Callable[[DamageAbstract], Dict[str, Any]]], Any]:
    def decorator(
        func: Callable[[DamageAbstract], Dict[str, Any]]
    ) -> Callable[[DamageAbstract], Dict[str, Any]]:
        PROCESSOR[weapon_id] = func
        _register_weapon(weapon_id, func)
        return func

    return decorator


def get_weapon(weapon_id: str) -> Callable[[DamageAbstract], Dict[str, Any]]:
    if weapon_id in PROCESSOR:
        return PROCESSOR[weapon_id]
    return _get_weapon(weapon_id)