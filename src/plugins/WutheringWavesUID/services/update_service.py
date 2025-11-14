# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/update_service.py

import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from nonebot.log import logger

from ..core.api.client import api_client
from ..database import get_cache, set_cache

# 日志数据源 (来自 draw_update_log.py)
LOG_API_URL = "https://gsuid.rth.app/WutheringWaves/update/log.json"
# 缓存 Key
CACHE_KEY = "wws_update_log"
# 缓存时间 (6小时)
CACHE_TIME = 3600 * 6


# --- Pydantic 模型 ---
class LogItem(BaseModel):
    title: str
    msg: List[str]


class LogResponse(BaseModel):
    code: int
    msg: str
    data: Dict[str, LogItem]  # { "v1.0.0": { ... } }


# --- 模型结束 ---


class UpdateService:
    """
    更新日志服务
    """

    async def get_update_log(self) -> Optional[Dict[str, LogItem]]:
        """获取并缓存更新日志"""

        # 1. 读缓存
        cached = await get_cache(CACHE_KEY)
        if cached:
            try:
                data = json.loads(cached)
                return {k: LogItem(**v) for k, v in data.items()}
            except Exception:
                pass  # 缓存解析失败，重新获取

        # 2. 爬取 API
        try:
            resp = await api_client.get(LOG_API_URL)
            resp.raise_for_status()
            data = resp.json()

            # 验证数据
            validated_data = LogResponse(**data)

            if validated_data.code == 200 and validated_data.data:
                # 3. 写缓存
                await set_cache(CACHE_KEY, json.dumps(validated_data.data), CACHE_TIME)
                # 直接返回 pydantic 实例
                return {k: LogItem(**v) for k, v in validated_data.data.items()}
            else:
                logger.error(f"Failed to fetch update log: {validated_data.msg}")
                return None

        except Exception as e:
            logger.error(f"Failed to fetch update log from API: {e}")
            return None


# 创建全局服务实例
update_service = UpdateService()