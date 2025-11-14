# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/gacha_service.py

import asyncio
import json
import time
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional, Tuple, List
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from nonebot.log import logger

from ..models import UserBind, WavesGacha
from ..database import async_session
from ..core.api.waves_api import waves_api

# 抽卡类型映射
GACHA_TYPE_MAP = {
  "1": "角色活动",
  "2": "武器活动",
  "3": "角色常驻",
  "4": "武器常驻",
  "5": "新手",
}
GACHA_TYPE_LIST = list(GACHA_TYPE_MAP.keys())


class GachaService:
  """抽卡记录服务"""

  def _parse_gacha_url(self, url: str) -> Optional[Dict[str, Any]]:
    """
    解析抽卡链接
    (迁移自 get_gachalogs.py -> GachaGet.parse_url)
    """
    try:
      parsed_url = urlparse(url)
      query_params = parse_qs(parsed_url.query)

      # API URL 的 base
      base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

      # 检查必要参数
      required_params = [
        "cardPoolId", "cardPoolType", "languageCode",
        "playerId", "serverId", "recordId"
      ]

      params = {"base_url": base_url}
      for param in required_params:
        if param not in query_params:
          logger.warning(f"抽卡链接缺少参数: {param}")
          return None
        params[param] = query_params[param][0]

      # playerId 即 uid
      params["uid"] = params["playerId"]
      return params

    except Exception as e:
      logger.error(f"解析抽卡链接失败: {e}")
      return None

  async def _get_latest_message_id(self, user_id: str, uid: str, gacha_type: str) -> Optional[str]:
    """获取数据库中最新的 messageId"""
    async with async_session() as session:
      result = await session.execute(
          select(WavesGacha.message_id)
          .where(WavesGacha.user_id == user_id, WavesGacha.uid == uid, WavesGacha.gacha_type == gacha_type)
          .order_by(WavesGacha.time.desc())
          .limit(1)
      )
      latest_record = result.scalar_one_or_none()
      return latest_record

  async def update_gacha_logs(self, user_id: str, gacha_url: str) -> str:
    """
    更新用户的抽卡记录
    (迁移自 get_gachalogs.py -> GachaGet.get_all_gacha)
    """
    # 1. 解析 URL
    url_params = self._parse_gacha_url(gacha_url)
    if not url_params:
      return "抽卡链接解析失败，请确保链接正确。"

    uid = url_params["uid"]
    base_url = url_params["base_url"]

    # 2. 检查此 UID 是否绑定到该用户
    bind_info = await self._check_user_uid_match(user_id, uid)
    if not bind_info:
      return f"此抽卡链接对应的 UID {uid} 未绑定到你的账号，请先绑定后再导入。"

    total_new_items = 0

    try:
      for gacha_type in GACHA_TYPE_LIST:
        logger.info(f"开始更新 {uid} 的 {GACHA_TYPE_MAP[gacha_type]} 卡池...")

        # 3. 查找数据库中该卡池的最新记录
        latest_msg_id = await self._get_latest_message_id(user_id, uid, gacha_type)

        end_id = "0"
        stop_flag = False

        while not stop_flag:
          # 4. 构造 API 请求
          api_params = {
            "playerId": uid,
            "cardPoolId": url_params["cardPoolId"],  # cardPoolId 似乎是通用的
            "cardPoolType": gacha_type,
            "languageCode": url_params["languageCode"],
            "serverId": url_params["serverId"],
            "recordId": url_params["recordId"],
            "endId": end_id,
          }

          response = await waves_api.get_gacha_logs(base_url, api_params)

          if not response.success or not isinstance(response.data, list):
            logger.warning(f"获取卡池 {gacha_type} 失败: {response.msg}")
            break  # 获取失败，跳到下一个卡池

          gacha_list = response.data
          if not gacha_list:
            break  # 没有更多数据

          new_items_batch = []

          for item in gacha_list:
            message_id = item.get("messageId")

            # 5. 查重
            if message_id == latest_msg_id:
              stop_flag = True
              break

            new_items_batch.append(WavesGacha(
                user_id=user_id,
                uid=uid,
                gacha_type=gacha_type,
                gacha_name=GACHA_TYPE_MAP[gacha_type],
                item_id=item.get("resourceId"),
                item_name=item.get("name"),
                item_type=item.get("resourceType"),
                rarity=item.get("quality"),
                time=item.get("time"),
                message_id=message_id,
            ))

          # 6. 批量插入数据库
          if new_items_batch:
            async with async_session() as session:
              async with session.begin():
                session.add_all(new_items_batch)
                try:
                  await session.commit()
                  total_new_items += len(new_items_batch)
                except IntegrityError:
                  await session.rollback()
                  logger.warning(f"导入卡池 {gacha_type} 时遇到重复 messageId，停止导入。")
                  stop_flag = True  # 遇到重复，停止
                except Exception as e:
                  await session.rollback()
                  logger.error(f"导入卡池 {gacha_type} 数据库出错: {e}")
                  stop_flag = True  # 数据库出错，停止

          # 7. 更新 end_id 以便翻页
          end_id = gacha_list[-1].get("messageId")

          if stop_flag:
            break  # 已找到最新记录

          await asyncio.sleep(0.5)  # 礼貌性延迟

      return f"抽卡记录导入完成！共新增 {total_new_items} 条记录。"

    except Exception as e:
      logger.error(f"更新抽卡记录时发生意外错误: {e}")
      return f"导入时发生错误: {e}"

  async def _check_user_uid_match(self, user_id: str, uid: str) -> Optional[UserBind]:
    """检查用户是否绑定了该UID"""
    async with async_session() as session:
      result = await session.execute(
          select(UserBind)
          .where(UserBind.user_id == user_id, UserBind.uid == uid)
      )
      return result.scalar_one_or_none()

  async def get_gacha_summary(self, user_id: str, uid: str) -> Dict[str, Any]:
    """
    从数据库读取并统计抽卡数据
    (迁移自 draw_gachalogs.py 的数据处理部分)
    """
    summary = {
      "uid": uid,
      "total": 0,
      "pools": []
    }

    async with async_session() as session:
      for gacha_type, gacha_name in GACHA_TYPE_MAP.items():
        stmt = (
          select(WavesGacha)
          .where(WavesGacha.user_id == user_id, WavesGacha.uid == uid, WavesGacha.gacha_type == gacha_type)
          .order_by(WavesGacha.time.asc())  # 按时间正序排列
        )
        result = await session.execute(stmt)
        records = result.scalars().all()

        if not records:
          continue

        total = len(records)
        summary["total"] += total

        pity_5 = 0  # 5星保底
        pity_4 = 0  # 4星保底
        star_5_list = []
        star_4_list = []

        for item in records:
          pity_5 += 1
          pity_4 += 1

          if item.rarity == 5:
            star_5_list.append({"name": item.item_name, "pity": pity_5})
            pity_5 = 0
            pity_4 = 0  # 抽到5星重置4星保底
          elif item.rarity == 4:
            star_4_list.append({"name": item.item_name, "pity": pity_4})
            pity_4 = 0

        avg_5_pity = (total - pity_5) / len(star_5_list) if star_5_list else 0

        summary["pools"].append({
          "name": gacha_name,
          "total": total,
          "star_5_count": len(star_5_list),
          "star_4_count": len(star_4_list),
          "pity_5": pity_5,
          "avg_5_pity": round(avg_5_pity, 1),
          "star_5_list": star_5_list
        })

    return summary


# 创建全局服务实例
gacha_service = GachaService()