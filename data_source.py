# nonebot_plugin_wws_uid/data_source.py

import httpx
import io
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import Config

# --- 全局资源加载 ---

# 获取插件的根目录
PLUGIN_DIR = Path(__file__).parent
ASSETS_DIR = PLUGIN_DIR / "assets"

# 加载字体
try:
  FONT_PATH = ASSETS_DIR / "HYWH-65W.ttf"
  FONT_30 = ImageFont.truetype(str(FONT_PATH), 30)
  FONT_25 = ImageFont.truetype(str(FONT_PATH), 25)
  FONT_20 = ImageFont.truetype(str(FONT_PATH), 20)
except Exception as e:
  logger.error(f"加载字体失败，请检查 assets 目录下是否存在 HYWH-65W.ttf 文件: {e}")
  # 提供一个降级方案，避免程序完全崩溃
  FONT_30 = FONT_25 = FONT_20 = ImageFont.load_default()

# 从驱动器中获取插件配置
plugin_config = Config.parse_obj(get_driver().config)


class WutheringWavesAPI:
  """鸣潮API请求封装"""

  def __init__(self, uid: str):
    self.uid = uid
    self.api_url = plugin_config.WWS_API_URL

  async def get_player_data(self) -> dict[str, Any]:
    """从API获取玩家数据"""
    headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
      "Content-Type": "application/json",
      "Accept": "application/json, text/plain, */*",
      "Referer": "https://www.kurobbs.com/",
      "Origin": "https://www.kurobbs.com",
    }
    payload = {"uid": self.uid}

    try:
      async with httpx.AsyncClient(proxies=plugin_config.WWS_PROXY) as client:
        response = await client.post(self.api_url, json=payload, headers=headers, timeout=15.0)
        response.raise_for_status()
        data = response.json()

      if data.get("code") != 200:
        raise ValueError(f"API返回错误: {data.get('msg', '未知错误')}")
      if not data.get("data"):
        raise ValueError("API未返回玩家数据，可能是UID错误或不存在")

      return data["data"]
    except httpx.RequestError as e:
      logger.error(f"请求API失败 (UID: {self.uid}): {e}")
      raise ConnectionError("网络请求失败，请稍后再试或检查代理设置")
    except ValueError as e:
      raise e
    except Exception as e:
      logger.error(f"处理API数据时发生未知错误 (UID: {self.uid}): {e}")
      raise RuntimeError("处理数据时发生内部错误")


async def generate_info_card(data: dict) -> MessageSegment:
  """根据玩家数据生成信息卡片图片"""
  try:
    bg_image = Image.open(ASSETS_DIR / "wws_bg.png").convert("RGBA")
  except FileNotFoundError:
    logger.error(f"背景图片 wws_bg.png 未找到，请检查 assets 目录")
    raise FileNotFoundError("插件资源文件缺失，无法生成图片")

  draw = ImageDraw.Draw(bg_image)

  # 提取数据
  nickname = data.get("nickname", "未知")
  uid = data.get("uid", "未知")