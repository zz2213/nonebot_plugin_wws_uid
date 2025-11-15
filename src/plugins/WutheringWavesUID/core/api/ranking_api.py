# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/api/ranking_api.py

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field
from .client import api_client  # 复用已有的 api_client
from .models import APIResponse  # 复用通用的 APIResponse
# --- 修复导入 ---
from ... import plugin_config

# --- 修复结束 ---

# --- 从 WutheringWavesUID1/utils/api/wwapi.py 迁移过来的常量 ---
# 关键修改：MAIN_URL 现在从配置中获取
MAIN_URL = plugin_config.WAVES_RANK_API_URL

UPLOAD_URL = f"{MAIN_URL}/top/waves/upload"
GET_RANK_URL = f"{MAIN_URL}/top/waves/rank"
GET_TOTAL_RANK_URL = f"{MAIN_URL}/top/waves/total/rank"
ONE_RANK_URL = f"{MAIN_URL}/top/waves/one"
UPLOAD_ABYSS_RECORD_URL = f"{MAIN_URL}/top/waves/abyss/upload"
GET_ABYSS_RECORD_URL = f"{MAIN_URL}/top/waves/abyss/record"
GET_HOLD_RATE_URL = f"{MAIN_URL}/api/waves/hold/rates"
GET_POOL_LIST = f"{MAIN_URL}/api/waves/pool/list"
GET_TOWER_APPEAR_RATE = f"{MAIN_URL}/api/waves/abyss/appear_rate"
UPLOAD_SLASH_RECORD_URL = f"{MAIN_URL}/top/waves/slash/upload"
GET_SLASH_APPEAR_RATE = f"{MAIN_URL}/api/waves/slash/appear_rate"
GET_SLASH_RANK_URL = f"{MAIN_URL}/top/waves/slash/rank"
# --- 常量修改结束 ---

ABYSS_TYPE = Literal["l4", "m4", "r4", "a"]

ABYSS_TYPE_MAP = {
    "残响之塔": "l",
    "深境之塔": "m",
    "回音之塔": "r",
}

ABYSS_TYPE_MAP_REVERSE = {
    "l4": "残响之塔 - 4层",
    "m4": "深境之塔 - 4层",
    "r4": "回音之塔 - 4层",
}


# --- Pydantic 模型 (省略大部分，保持一致) ---
# ... (所有 Pydantic 模型保持不变) ...

class RankDetail(BaseModel):
    rank: int
    user_id: str
    username: str
    alias_name: str
    kuro_name: str
    waves_id: str
    char_id: int
    level: int
    chain: int
    weapon_id: int
    weapon_level: int
    weapon_reson_level: int
    sonata_name: str
    phantom_score: float
    phantom_score_bg: str
    expected_damage: float
    expected_name: str


class RankInfoData(BaseModel):
    details: List[RankDetail]
    page: int
    page_num: int


class RankInfoResponse(BaseModel):
    code: int
    message: str
    data: Optional[RankInfoData] = None


# ... (省略所有中间模型) ...

class SlashAppearRateResponse(BaseModel):
    code: int
    message: str
    data: List["SlashAppearRate"]


class RankingAPI:
    """鸣潮排行榜API封装"""

    async def get_rank(self, rank_item: RankItem) -> RankInfoResponse:
        """获取角色排行"""
        result = await api_client.request("POST", GET_RANK_URL, json=rank_item.dict())
        return RankInfoResponse(**result)

    async def get_total_rank(self, total_rank_request: TotalRankRequest) -> TotalRankResponse:
        """获取总分排行"""
        result = await api_client.request("POST", GET_TOTAL_RANK_URL, json=total_rank_request.dict())
        return TotalRankResponse(**result)

    # ... (省略所有其他 API 方法) ...

    async def get_pool_list(self) -> PoolResponse:
        """获取卡池统计"""
        # GET_POOL_LIST 是 GET 请求
        result = await api_client.request("GET", GET_POOL_LIST)
        return PoolResponse(**result)

    async def upload_data(self, data: dict) -> APIResponse:
        """上传面板数据"""
        result = await api_client.request("POST", UPLOAD_URL, json=data)
        return APIResponse(
            success=result.get("code") == 200,
            msg=result.get("message", "上传失败"),
            data=result.get("data", {})
        )


ranking_api = RankingAPI()