# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/utils.py
from typing import Dict, Any, Optional

# 适配修改：
from ...models import PlayerInfo
from nonebot.log import logger
# from gsuid_core.data_store import get_data_store # 移除 gsuid_core 依赖
# from utils.map.damage.damage import get_damage_data as _get_damage_data # 下方修复
from ..data.damage.damage import get_damage_data as _get_damage_data


async def get_player_info(uid: str) -> Optional[PlayerInfo]:
  # 适配修改：
  # 移除了 gsuid_core 的数据库调用
  # 这里的逻辑需要被 service 层的数据库调用所替换
  # 目前暂时返回 None，并打印一个警告

  logger.warning(
      f"[Damage Calc] get_player_info stub called for uid {uid}. "
      "This function must be refactored to use UserService to fetch PlayerInfo from the database."
  )

  # store = await get_data_store()
  # player = await store.get_player_info_by_uid(uid)
  # return player

  return None


def get_damage_data(char_id: str) -> Dict[str, Any]:
  return _get_damage_data(char_id)