# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/game_service.py

from typing import Optional, Dict, Any, List
import json

from ..core.api.waves_api import waves_api
from ..core.api.ranking_api import (
  ranking_api, RankItem, RankInfoResponse, TotalRankRequest,
  TotalRankResponse, AbyssRecordRequest, AbyssRecordResponse,
  RoleHoldRateRequest, RoleHoldRateResponse, SlashRankItem, SlashRankRes
)
from ..database import get_cache, set_cache


class GameService:
  """游戏数据服务"""

  # --- 现有的方法 (来自 waves_api) ---

  async def get_user_info(self, cookie: str, uid: str) -> Dict[str, Any]:
    """获取用户信息 (来自游戏API)"""
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
    """获取角色信息 (来自游戏API)"""
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
    """获取游戏统计 (来自游戏API)"""
    cache_key = f"game_stats_{uid}"
    cached = await get_cache(cache_key)

    if cached:
      return json.loads(cached)

    result = await waves_api.get_stats(cookie, uid)
    if result.success:
      await set_cache(cache_key, json.dumps(result.data), 600)  # 10分钟缓存
      return result.data
    return {}

  async def get_explore_info(self, cookie: str, uid: str) -> Dict[str, Any]:
    """获取探索度信息 (来自游戏API)"""
    cache_key = f"explore_info_{uid}"
    cached = await get_cache(cache_key)

    if cached:
      return json.loads(cached)

    result = await waves_api.get_explore_info(cookie, uid)
    if result.success:
      await set_cache(cache_key, json.dumps(result.data), 1800)  # 缓存30分钟
      return result.data
    return {}

  # --- 新增深渊相关方法 (来自 waves_api) ---
  async def get_tower_info(self, cookie: str, uid: str) -> Dict[str, Any]:
    """获取深境之塔信息 (来自游戏API)"""
    cache_key = f"tower_info_{uid}"
    cached = await get_cache(cache_key)
    if cached:
      return json.loads(cached)
    result = await waves_api.get_tower_info(cookie, uid)
    if result.success:
      await set_cache(cache_key, json.dumps(result.data), 1800)  # 缓存30分钟
      return result.data
    return {}

  async def get_challenge_info(self, cookie: str, uid: str) -> Dict[str, Any]:
    """获取全息战略信息 (来自游戏API)"""
    cache_key = f"challenge_info_{uid}"
    cached = await get_cache(cache_key)
    if cached:
      return json.loads(cached)
    result = await waves_api.get_challenge_info(cookie, uid)
    if result.success:
      await set_cache(cache_key, json.dumps(result.data), 1800)  # 缓存30分钟
      return result.data
    return {}

  async def get_slash_info(self, cookie: str, uid: str) -> Dict[str, Any]:
    """获取冥歌海墟信息 (来自游戏API)"""
    cache_key = f"slash_info_{uid}"
    cached = await get_cache(cache_key)
    if cached:
      return json.loads(cached)
    result = await waves_api.get_slash_info(cookie, uid)
    if result.success:
      await set_cache(cache_key, json.dumps(result.data), 1800)  # 缓存30分钟
      return result.data
    return {}

  # --- 新增方法结束 ---

  # --- 现有的方法 (来自 ranking_api) ---

  async def get_character_rank(self, rank_item: RankItem) -> Optional[RankInfoResponse]:
    """获取角色排行 (来自排行API)"""
    cache_key = f"rank_{rank_item.char_id}_{rank_item.rank_type}_{rank_item.page}"
    cached = await get_cache(cache_key)
    if cached:
      return RankInfoResponse(**json.loads(cached))

    result = await ranking_api.get_rank(rank_item)
    if result.code == 200 and result.data:
      await set_cache(cache_key, result.json(), 1800)
      return result
    return None

  async def get_total_rank(self, total_rank_request: TotalRankRequest) -> Optional[TotalRankResponse]:
    """获取总分排行 (来自排行API)"""
    cache_key = f"total_rank_{total_rank_request.page}"
    cached = await get_cache(cache_key)
    if cached:
      return TotalRankResponse(**json.loads(cached))

    result = await ranking_api.get_total_rank(total_rank_request)
    if result.code == 200 and result.data:
      await set_cache(cache_key, result.json(), 1800)
      return result
    return None

  async def get_abyss_usage_rate(self, abyss_request: AbyssRecordRequest) -> Optional[AbyssRecordResponse]:
    """获取深渊使用率 (来自排行API)"""
    cache_key = f"abyss_rate_{abyss_request.abyss_type}"
    cached = await get_cache(cache_key)
    if cached:
      return AbyssRecordResponse(**json.loads(cached))

    result = await ranking_api.get_abyss_record(abyss_request)
    if result.code == 200 and result.data:
      await set_cache(cache_key, result.json(), 3600 * 6)
      return result
    return None

  async def get_character_hold_rate(self, hold_rate_request: RoleHoldRateRequest) -> Optional[RoleHoldRateResponse]:
    """获取角色持有率 (来自排行API)"""
    char_id = hold_rate_request.char_id if hold_rate_request.char_id else "all"
    cache_key = f"hold_rate_{char_id}"
    cached = await get_cache(cache_key)
    if cached:
      return RoleHoldRateResponse(**json.loads(cached))

    result = await ranking_api.get_hold_rate(hold_rate_request)
    if result.code == 200 and result.data:
      await set_cache(cache_key, result.json(), 3600 * 6)
      return result
    return None

  async def get_slash_rank(self, slash_rank_item: SlashRankItem) -> Optional[SlashRankRes]:
    """获取冥海排行 (来自排行API)"""
    cache_key = f"slash_rank_{slash_rank_item.page}"
    cached = await get_cache(cache_key)
    if cached:
      return SlashRankRes(**json.loads(cached))

    result = await ranking_api.get_slash_rank(slash_rank_item)
    if result.code == 200 and result.data:
      await set_cache(cache_key, result.json(), 1800)
      return result
    return None

  async def upload_panel_data(self, cookie: str, uid: str) -> str:
    """
    上传面板数据
    这是一个示例流程：先获取角色信息，然后上传
    """
    role_data = await self.get_role_info(cookie, uid)
    if not role_data:
      return "获取角色信息失败，无法上传"

    upload_data = {
      "uid": uid,
      "role_list": role_data.get("roleList", [])
    }

    result = await ranking_api.upload_data(upload_data)
    return result.msg