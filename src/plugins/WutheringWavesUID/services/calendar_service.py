# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/calendar_service.py

import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from nonebot.log import logger

from ..core.api.client import api_client
from ..database import get_cache, set_cache

# --- Pydantic 模型 (迁移自 calendar_model.py) ---
CALENDAR_URL = "https://gsuid.rth.app/WutheringWaves/calendar"


class Develop(BaseModel):
  char: List[int]
  weapon: List[int]


class CalendarData(BaseModel):
  id: int
  weekday: str
  develop: Develop
  tower: str
  pool: List
  event: List


class CalendarResponse(BaseModel):
  code: int
  msg: str
  data: CalendarData


# --- 模型结束 ---


class CalendarService:
  """
  日历服务
  负责从 gsuid.rth.app 获取日历数据 (包含每日材料)
  """

  async def get_calendar_data(self) -> Optional[CalendarData]:
    """获取并缓存日历数据"""
    cache_key = "wws_calendar_data"
    cached = await get_cache(cache_key)
    if cached:
      try:
        return CalendarData(**json.loads(cached))
      except Exception:
        pass  # 缓存解析失败，重新获取

    try:
      resp = await api_client.get(CALENDAR_URL)
      resp.raise_for_status()
      data = resp.json()

      # 验证数据
      validated_data = CalendarResponse(**data)

      if validated_data.code == 200 and validated_data.data:
        # 缓存6小时
        await set_cache(cache_key, validated_data.data.json(), 3600 * 6)
        return validated_data.data
      else:
        logger.error(f"Failed to fetch calendar data: {validated_data.msg}")
        return None

    except Exception as e:
      logger.error(f"Failed to fetch calendar data from API: {e}")
      return None


# 创建全局服务实例
calendar_service = CalendarService()