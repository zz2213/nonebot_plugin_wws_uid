from typing import Optional
from ..database import create_or_update_user, get_user_by_user_id
from ..models import WavesUser

class UserService:
    """用户服务"""

    async def create_or_update_user(
        self,
        user_id: str,
        bot_id: str,
        uid: str,
        cookie: str,
        did: str
    ) -> Optional[WavesUser]:
        """创建或更新用户"""
        return await create_or_update_user(user_id, bot_id, uid, cookie, did)

    async def get_user(self, user_id: str, bot_id: str) -> Optional[WavesUser]:
        """获取用户"""
        return await get_user_by_user_id(user_id, bot_id)

    async def update_user_cookie(self, user_id: str, bot_id: str, cookie: str) -> bool:
        """更新用户Cookie"""
        user = await self.get_user(user_id, bot_id)
        if user:
            user.cookie = cookie
            # 这里需要实现保存逻辑
            return True
        return False