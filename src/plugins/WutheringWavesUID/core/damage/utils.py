# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/utils.py
from typing import Dict, Any, Optional

# 适配修改：
# --- 修复：移除 PlayerInfo ---
# from ...models import PlayerInfo # 错误：此模型已不存在
# --- 修复结束 ---
from nonebot.log import logger
from ..data.damage.damage import get_damage_data as _get_damage_data


async def get_player_info(uid: str) -> Optional[Any]: # 修复：类型改为 Any
    """
    (桩函数)
    此函数来自旧的 gsuid_core 框架，
    在我们的新框架 (core/damage/damage.py) 中已不再需要。
    保留此文件仅为防止 core/damage/register_*.py 导入失败。
    """
    logger.warning(
        f"[Damage Calc] get_player_info stub called for uid {uid}. "
        "This function is deprecated and should not be used."
    )
    return None


def get_damage_data(char_id: str) -> Dict[str, Any]:
    return _get_damage_data(char_id)