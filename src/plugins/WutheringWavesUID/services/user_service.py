# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/user_service.py

import uuid
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..database import async_session
from ..models import User, UserBind
from ..core.api.waves_api import waves_api
from ..core.api.models import APIResponse, LoginResponse


class UserService:

  async def get_user_bind(self, user_id: str) -> Optional[UserBind]:
    """获取用户当前绑定的UID信息"""
    async with async_session() as session:
      # 1. 查找用户
      user_result = await session.execute(
          select(User).where(User.user_id == user_id)
      )
      user: Optional[User] = user_result.scalar_one_or_none()

      if not user or not user.current_bind_uid:
        # 2. 如果没有当前绑定, 尝试获取第一个
        first_bind_result = await session.execute(
            select(UserBind).where(UserBind.user_id == user_id).limit(1)
        )
        first_bind = first_bind_result.scalar_one_or_none()
        if first_bind:
          # 自动将其设为当前绑定
          await self.set_current_bind(user_id, first_bind.uid)
          return first_bind
        return None

      # 3. 获取当前绑定的信息
      bind_result = await session.execute(
          select(UserBind).where(
              UserBind.user_id == user_id,
              UserBind.uid == user.current_bind_uid
          )
      )
      return bind_result.scalar_one_or_none()

  async def create_user_bind(self, user_id: str, uid: str, cookie: str) -> bool:
    """创建或更新用户绑定"""
    async with async_session() as session:
      async with session.begin():
        # 1. 查找现有绑定
        bind_result = await session.execute(
            select(UserBind).where(UserBind.user_id == user_id, UserBind.uid == uid)
        )
        existing_bind: Optional[UserBind] = bind_result.scalar_one_or_none()

        if existing_bind:
          existing_bind.cookie = cookie
        else:
          new_bind = UserBind(user_id=user_id, uid=uid, cookie=cookie)
          session.add(new_bind)

        # 2. 查找或创建主用户
        user_result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user: Optional[User] = user_result.scalar_one_or_none()

        if user:
          user.current_bind_uid = uid
        else:
          new_user = User(user_id=user_id, current_bind_uid=uid)
          session.add(new_user)

      await session.commit()
      return True

  async def set_current_bind(self, user_id: str, uid: str) -> bool:
    """设置当前绑定的UID"""
    async with async_session() as session:
      async with session.begin():
        # 1. 检查此绑定是否存在
        bind_result = await session.execute(
            select(UserBind).where(UserBind.user_id == user_id, UserBind.uid == uid)
        )
        if not bind_result.scalar_one_or_none():
          return False  # 绑定不存在

        # 2. 更新或创建 User
        user_result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user: Optional[User] = user_result.scalar_one_or_none()

        if user:
          user.current_bind_uid = uid
        else:
          new_user = User(user_id=user_id, current_bind_uid=uid)
          session.add(new_user)

      await session.commit()
      return True

  # --- 新增方法 (来自 wutheringwaves_login/login.py) ---

  async def get_captcha(self, phone: str) -> APIResponse:
    """
    调用 API 获取验证码
    """
    return await waves_api.get_captcha_code(phone)

  async def login_by_phone(self, user_id: str, phone: str, code: str) -> LoginResponse:
    """
    使用手机和验证码登录, 并自动绑定
    """
    # 生成一个随机 deviceId (did)
    did = str(uuid.uuid4())

    # 1. 调用 API 登录
    login_response = await waves_api.login(phone, code, did)

    # 2. 登录成功, 自动绑定
    if login_response.success:
      user_info = login_response.user_info
      if user_info:
        uid = user_info.get("uid")
        cookie = f"token={login_response.token}"  # 构造 cookie
        if uid:
          await self.create_user_bind(user_id, uid, cookie)
          # 附加 UID 到消息中
          login_response.msg = f"登录成功！已自动为您绑定 UID: {uid}"

    return login_response
  # --- 新增方法结束 ---


# 创建全局服务实例
user_service = UserService()