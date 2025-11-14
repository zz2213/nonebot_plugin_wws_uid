# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/wiki_service.py

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import lru_cache
from nonebot.log import logger

from ..core.api.client import api_client
from ..database import get_cache, set_cache

# API (来自 wutheringwaves_wiki/guide.py)
GUIDE_API_URL = "https://api.kurocn.com/wiki/wiki/list"

# 本地数据路径
DATA_PATH = Path(__file__).parent.parent / "core" / "data"
CHAR_WIKI_PATH = DATA_PATH / "detail_json" / "char"
WEAPON_WIKI_PATH = DATA_PATH / "detail_json" / "weapon"
ECHO_WIKI_PATH = DATA_PATH / "detail_json" / "echo"
SONATA_WIKI_PATH = DATA_PATH / "detail_json" / "sonata"
ID_NAME_MAP_PATH = DATA_PATH / "id2name.json"


@lru_cache()
def get_id_name_map() -> Dict[str, str]:
  """加载 id2name.json"""
  try:
    with open(ID_NAME_MAP_PATH, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception:
    return {}


class WikiService:
  """
  Wiki 资料服务
  """

  def __init__(self):
    self.id_name_map = get_id_name_map()
    self.name_id_map = {v: k for k, v in self.id_name_map.items()}

  def _get_std_name(self, name: str) -> str:
    """获取标准名称 (临时)"""
    # TODO: 应接入 AliasService
    return name

  async def get_char_wiki_data(self, name: str) -> Optional[Dict[str, Any]]:
    """获取角色 Wiki 数据"""
    std_name = self._get_std_name(name)

    # 尝试通过名字获取ID
    char_id = self.name_id_map.get(std_name)
    if not char_id:
      logger.warning(f"未在 id2name.json 中找到角色: {std_name}")
      # 尝试直接用名字作为文件名 (兜底)
      file_path = CHAR_WIKI_PATH / f"{std_name}.json"
      if not file_path.exists():
        return None
    else:
      file_path = CHAR_WIKI_PATH / f"{char_id}.json"
      if not file_path.exists():
        return None

    try:
      with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        data["id"] = file_path.stem  # 注入ID
        return data
    except Exception as e:
      logger.error(f"加载角色 Wiki JSON 失败 ({file_path}): {e}")
      return None

  async def get_weapon_wiki_data(self, name: str) -> Optional[Dict[str, Any]]:
    """获取武器 Wiki 数据"""
    std_name = self._get_std_name(name)

    weapon_id = self.name_id_map.get(std_name)
    if not weapon_id:
      logger.warning(f"未在 id2name.json 中找到武器: {std_name}")
      return None  # 武器必须用ID

    file_path = WEAPON_WIKI_PATH / f"{weapon_id}.json"
    if not file_path.exists():
      return None

    try:
      with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        data["id"] = file_path.stem  # 注入ID
        return data
    except Exception as e:
      logger.error(f"加载武器 Wiki JSON 失败 ({file_path}): {e}")
      return None

  async def get_echo_wiki_data(self, name: str) -> Optional[Dict[str, Any]]:
    """获取声骸/套装 Wiki 数据"""
    std_name = self._get_std_name(name)

    # 优先检查是不是套装
    file_path = SONATA_WIKI_PATH / f"{std_name}.json"
    if file_path.exists():
      try:
        with open(file_path, "r", encoding="utf-8") as f:
          data = json.load(f)
          data["name"] = std_name
          data["type"] = "sonata"  # 标记为套装
          return data
      except Exception as e:
        logger.error(f"加载套装 Wiki JSON 失败 ({file_path}): {e}")

    # 检查是不是声骸
    echo_id = self.name_id_map.get(std_name)
    if not echo_id:
      return None  # 找不到

    file_path = ECHO_WIKI_PATH / f"{echo_id}.json"
    if not file_path.exists():
      return None

    try:
      with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        data["id"] = file_path.stem  # 注入ID
        data["name"] = std_name
        data["type"] = "echo"  # 标记为单个声骸
        return data
    except Exception as e:
      logger.error(f"加载声骸 Wiki JSON 失败 ({file_path}): {e}")
      return None

  async def get_guide_images(self, char_name: str) -> Optional[List[str]]:
    """
    获取角色攻略图
    (迁移自 wutheringwaves_wiki/guide.py)
    """
    cache_key = f"guide_images_{char_name}"
    cached = await get_cache(cache_key)
    if cached:
      return json.loads(cached)

    params = {"name": char_name}
    try:
      # 使用 api_client 请求
      resp = await api_client.request("GET", GUIDE_API_URL, params=params)

      if resp.get("code") == 200:
        img_urls = [item.get("url") for item in resp.get("data", []) if item.get("url")]
        if img_urls:
          await set_cache(cache_key, json.dumps(img_urls), 3600 * 6)  # 缓存6小时
          return img_urls

      logger.warning(f"获取攻略图 API 失败: {resp}")
      return None
    except Exception as e:
      logger.error(f"请求攻略图 API 失败: {e}")
      return None


# 创建全局服务实例
wiki_service = WikiService()