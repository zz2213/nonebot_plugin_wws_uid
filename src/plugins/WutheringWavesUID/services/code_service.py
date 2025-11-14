# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/code_service.py

import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from nonebot.log import logger

from ..core.api.client import api_client
from ..database import get_cache, set_cache

# 兑换码数据源 (来自 wutheringwaves_code/__init__.py)
CODE_API_URL = "https://gsuid.rth.app/WutheringWaves/ann/code"
# 缓存 Key
CACHE_KEY = "wws_redemption_codes"
# 缓存时间 (6小时)
CACHE_TIME = 3600 * 6


# --- Pydantic 模型 ---
class CodeItem(BaseModel):
    code: str
    text: str


class CodeResponse(BaseModel):
    code: int
    msg: str
    data: List[CodeItem]


# --- 模型结束 ---


class CodeService:
    """
    兑换码服务
    负责从 gsuid.rth.app 获取兑换码数据
    """

    async def get_redemption_codes(self) -> Optional[List[CodeItem]]:
        """获取并缓存兑换码数据"""

        # 1. 读缓存
        cached = await get_cache(CACHE_KEY)
        if cached:
            try:
                # 缓存中直接存 List[CodeItem] 的 json
                data = json.loads(cached)
                return [CodeItem(**item) for item in data]
            except Exception:
                pass  # 缓存解析失败，重新获取

        # 2. 爬取 API
        try:
            resp = await api_client.get(CODE_API_URL)
            resp.raise_for_status()
            data = resp.json()

            # 验证数据
            validated_data = CodeResponse(**data)

            if validated_data.code == 200 and validated_data.data:
                # 3. 写缓存
                await set_cache(CACHE_KEY, json.dumps([item.dict() for item in validated_data.data]), CACHE_TIME)
                return validated_data.data
            else:
                logger.error(f"Failed to fetch redeem codes: {validated_data.msg}")
                return None

        except Exception as e:
            logger.error(f"Failed to fetch redeem codes from API: {e}")
            return None


# 创建全局服务实例
code_service = CodeService()