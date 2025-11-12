from typing import Optional, Dict, Any
from ..core.api.waves_api import waves_api
from ..database import get_cache, set_cache
import json

class GameService:
    """游戏数据服务"""

    async def get_user_info(self, cookie: str, uid: str) -> Dict[str, Any]:
        """获取用户信息"""
        cache_key = f"user_info_{uid}"
        cached = await get_cache(cache_key)

        if cached:
            return json.loads(cached)

        result = await waves_api.get_user_info(cookie, uid)
        if result.success:
            await set_cache(cache_key, json.dumps(result.data), 300)  # 5分钟缓存
            return result.data
        return {}

    async def get_role_info(self, cookie: str, uid: str) -> Dict[str, Any]:
        """获取角色信息"""
        cache_key = f"role_info_{uid}"
        cached = await get_cache(cache_key)

        if cached:
            return json.loads(cached)

        result = await waves_api.get_role_info(cookie, uid)
        if result.success:
            await set_cache(cache_key, json.dumps(result.data), 300)
            return result.data
        return {}

    async def get_game_stats(self, cookie: str, uid: str) -> Dict[str, Any]:
        """获取游戏统计"""
        cache_key = f"game_stats_{uid}"
        cached = await get_cache(cache_key)

        if cached:
            return json.loads(cached)

        result = await waves_api.get_stats(cookie, uid)
        if result.success:
            await set_cache(cache_key, json.dumps(result.data), 600)  # 10分钟缓存
            return result.data
        return {}