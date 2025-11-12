from ..database import bind_user, get_uid_by_user

class BindService:
    """绑定服务"""

    async def bind_user(
        self,
        user_id: str,
        bot_id: str,
        uid: str,
        group_id: str = ""
    ) -> bool:
        """绑定用户UID"""
        return await bind_user(user_id, bot_id, uid, group_id)

    async def get_user_uid(self, user_id: str, bot_id: str) -> str | None:
        """获取用户绑定的UID"""
        return await get_uid_by_user(user_id, bot_id)