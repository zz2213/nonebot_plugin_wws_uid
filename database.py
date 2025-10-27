from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from nonebot_plugin_datastore import get_session

from .models import WwsBind


# 使用 get_session 来安全地获取数据库会话
async def get_or_create_binding(user_id: str) -> tuple[WwsBind, bool]:
  """获取或创建用户的绑定信息"""
  async with get_session() as session:
    statement = select(WwsBind).where(WwsBind.user_id == user_id)
    result = await session.execute(statement)
    binding = result.scalar_one_or_none()

    if binding:
      return binding, False  # 已存在
    else:
      new_binding = WwsBind(user_id=user_id)
      session.add(new_binding)
      await session.commit()
      await session.refresh(new_binding)
      return new_binding, True  # 新创建


async def bind_uid(user_id: str, game_uid: str):
  """为用户绑定游戏UID"""
  async with get_session() as session:
    binding, _ = await get_or_create_binding(user_id)
    binding.game_uid = game_uid
    await session.commit()


async def get_uid(user_id: str) -> str | None:
  """获取用户绑定的游戏UID"""
  async with get_session() as session:
    statement = select(WwsBind.game_uid).where(WwsBind.user_id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()