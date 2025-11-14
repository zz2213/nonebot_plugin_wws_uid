# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/api/ranking_api.py

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field
from .client import api_client  # 复用已有的 api_client
from .models import APIResponse  # 复用通用的 APIResponse

# --- 从 WutheringWavesUID1/utils/api/wwapi.py 迁移过来的常量 ---

MAIN_URL = "https://top.camellya.xyz"
# MAIN_URL = "http://127.0.0.1:9001"

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


# --- 从 WutheringWavesUID1/utils/api/wwapi.py 迁移过来的 Pydantic 模型 ---

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


class RankItem(BaseModel):
  char_id: int
  page: int
  page_num: int
  rank_type: int
  waves_id: Optional[str] = ""
  version: str


class TotalRankRequest(BaseModel):
  page: int = Field(..., description="页码")
  page_num: int = Field(..., description="每页数量")
  version: str = Field(..., description="版本号")
  waves_id: str = Field(..., description="鸣潮id")


class CharScoreDetail(BaseModel):
  char_id: int
  phantom_score: float


class TotalRankDetail(BaseModel):
  rank: int
  user_id: str
  username: str
  alias_name: str
  kuro_name: str
  waves_id: str
  total_score: float
  char_score_details: List[CharScoreDetail]


class TotalRankInfoData(BaseModel):
  score_details: List[TotalRankDetail]
  page: int
  page_num: int


class TotalRankResponse(BaseModel):
  code: int
  message: str
  data: Optional[TotalRankInfoData] = None


class OneRankRequest(BaseModel):
  char_id: int = Field(..., description="角色ID")
  waves_id: Optional[str] = Field(default="", description="鸣潮ID")


class OneRankResponse(BaseModel):
  code: int
  message: str
  data: List[RankDetail]


class AbyssDetail(BaseModel):
  area_type: ABYSS_TYPE
  area_name: str
  floor: int
  char_ids: List[int]


class AbyssItem(BaseModel):
  waves_id: str
  abyss_record: List[AbyssDetail]
  version: str


class AbyssRecordRequest(BaseModel):
  abyss_type: ABYSS_TYPE


class AbyssUseRate(BaseModel):
  char_id: int
  rate: float


class AbyssRecord(BaseModel):
  abyss_type: ABYSS_TYPE
  use_rate: List[AbyssUseRate]


class AbyssRecordResponse(BaseModel):
  code: int
  message: str
  data: List[AbyssRecord]


class RoleHoldRate(BaseModel):
  char_id: int
  rate: float
  chain_rate: Dict[int, float]


class RoleHoldRateRequest(BaseModel):
  char_id: Optional[int] = None


class RoleHoldRateResponse(BaseModel):
  code: int
  message: str
  data: List[RoleHoldRate]


class SlashDetail(BaseModel):
  buffIcon: str
  buffName: str
  buffQuality: int
  charIds: List[int]
  score: int


class SlashDetailRequest(BaseModel):
  wavesId: str
  challengeId: int
  challengeName: str
  halfList: List[SlashDetail]
  rank: str
  score: int


class SlashRankItem(BaseModel):
  page: int
  page_num: int
  waves_id: str
  version: str


class SlashCharDetail(BaseModel):
  char_id: int
  level: int
  chain: int


class SlashHalfList(BaseModel):
  buff_icon: str
  buff_name: str
  buff_quality: int
  char_detail: List[SlashCharDetail]
  score: int


class SlashRank(BaseModel):
  half_list: List[SlashHalfList]
  score: int
  rank: int
  user_id: str
  waves_id: str
  kuro_name: str
  alias_name: str


class SlashRankData(BaseModel):
  page: int
  page_num: int
  start_date: str
  rank_list: List[SlashRank]


class SlashRankRes(BaseModel):
  code: int
  message: str
  data: Optional[SlashRankData] = None


# --- 新增 冥海出场率 模型 ---
class SlashAppearRateRequest(BaseModel):
  version: Optional[str] = None  # 似乎不需要参数，但保留


class SlashAppearRate(BaseModel):
  char_id: int
  rate: float


class SlashAppearRateResponse(BaseModel):
  code: int
  message: str
  data: List[SlashAppearRate]


# --- 新增模型结束 ---


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

  async def get_one_rank(self, one_rank_request: OneRankRequest) -> OneRankResponse:
    """获取单个角色排行"""
    result = await api_client.request("POST", ONE_RANK_URL, json=one_rank_request.dict())
    return OneRankResponse(**result)

  async def get_abyss_record(self, abyss_request: AbyssRecordRequest) -> AbyssRecordResponse:
    """获取深渊记录"""
    result = await api_client.request("POST", GET_ABYSS_RECORD_URL, json=abyss_request.dict())
    return AbyssRecordResponse(**result)

  # --- 新增 冥海出场率 API ---
  async def get_slash_appear_rate(self, request_data: SlashAppearRateRequest) -> SlashAppearRateResponse:
    """获取冥海出场率"""
    result = await api_client.request("POST", GET_SLASH_APPEAR_RATE, json=request_data.dict())
    return SlashAppearRateResponse(**result)

  # --- 新增 API 结束 ---

  async def get_hold_rate(self, hold_rate_request: RoleHoldRateRequest) -> RoleHoldRateResponse:
    """获取角色持有率"""
    result = await api_client.request("POST", GET_HOLD_RATE_URL, json=hold_rate_request.dict())
    return RoleHoldRateResponse(**result)

  async def get_slash_rank(self, slash_rank_item: SlashRankItem) -> SlashRankRes:
    """获取冥海排行"""
    result = await api_client.request("POST", GET_SLASH_RANK_URL, json=slash_rank_item.dict())
    return SlashRankRes(**result)

  async def upload_data(self, data: dict) -> APIResponse:
    """上传面板数据"""
    result = await api_client.request("POST", UPLOAD_URL, json=data)
    return APIResponse(
        success=result.get("code") == 200,
        msg=result.get("message", "上传失败"),
        data=result.get("data", {})
    )


ranking_api = RankingAPI()