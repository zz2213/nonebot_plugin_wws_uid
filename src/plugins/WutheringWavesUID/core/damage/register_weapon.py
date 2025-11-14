# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/register_weapon.py

from typing import Any, Callable, Dict, Optional
from .abstract import DamageAbstract

PROCESSOR: Dict[str, Callable[[DamageAbstract], Dict[str, Any]]] = {}

def register_weapon(
    weapon_id: str,
) -> Callable[[Callable[[DamageAbstract], Dict[str, Any]]], Any]:
    """
    (Framework A) 注册武器面板计算脚本
    """
    def decorator(
        func: Callable[[DamageAbstract], Dict[str, Any]]
    ) -> Callable[[DamageAbstract], Dict[str, Any]]:
        PROCESSOR[weapon_id] = func
        return func

    return decorator


def get_weapon(weapon_id: str) -> Optional[Callable[[DamageAbstract], Dict[str, Any]]]:
    """
    (Framework A) 获取武器面板计算脚本
    """
    return PROCESSOR.get(weapon_id)