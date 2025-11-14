# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/announcement_service.py

import json
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from nonebot.log import logger

from ..core.api.client import api_client
from ..database import get_cache, set_cache

# --- Pydantic 模型 (基于 ann_card.py 分析) ---
ANN_LIST_URL = "https://gsuid.rth.app/WutheringWaves/ann/list"
ANN_PIC_URL_TPL = "https://gsuid.rth.app/WutheringWaves/ann/pic/{}.png"


class AnnItem(BaseModel):
    id: int
    title: str
    pic_url: str  # 我们将自己构造这个


class AnnListResponse(BaseModel):
    code: int
    msg: str
    data: List[Dict[str, Any]]  # 原始数据是 [ {"id": 123, "title": "..."} ]


# --- 模型结束 ---


class AnnouncementService:
    """
    公告服务
    负责从 gsuid.rth.app 获取公告数据
    """

    async def get_announcements(self) -> Optional[List[AnnItem]]:
        """获取并缓存公告列表"""
        cache_key = "wws_announcement_list"
        cached = await get_cache(cache_key)
        if cached:
            try:
                # 缓存的是 List[AnnItem] 的 JSON
                items_data = json.loads(cached)
                return [AnnItem(**item) for item in items_data]
            except Exception:
                pass  # 缓存解析失败，重新获取

        try:
            resp = await api_client.get(ANN_LIST_URL)
            resp.raise_for_status()
            data = resp.json()

            validated_data = AnnListResponse(**data)

            if validated_data.code == 200 and validated_data.data:
                processed_list = []
                for item in validated_data.data:
                    ann_id = item.get("id")
                    if ann_id:
                        processed_list.append(AnnItem(
                            id=ann_id,
                            title=item.get("title", "无标题"),
                            pic_url=ANN_PIC_URL_TPL.format(ann_id)
                        ))

                # 缓存1小时
                await set_cache(cache_key, json.dumps([p.dict() for p in processed_list]), 3600)
                return processed_list
            else:
                logger.error(f"Failed to fetch announcement list: {validated_data.msg}")
                return None

        except Exception as e:
            logger.error(f"Failed to fetch announcement API: {e}")
            return None


# 创建全局服务实例
announcement_service = AnnouncementService()