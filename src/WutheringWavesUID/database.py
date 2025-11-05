from sqlalchemy import select
from nonebot_plugin_datastore import get_session
from .models import WwsBind, WwsUser

async def get_uid_by_user(user_id: str, bot_id: str) -> str | None:
    """通过用户ID获取绑定的UID"""
    async with get_session() as session:
        result = await session.scalar(
            select(WwsBind.game_uid).where(
                WwsBind.user_id == user_id,
                WwsBind.bot_id == bot_id
            )
        )
        return result

async def bind_uid(user_id: str, bot_id: str, uid: str, group_id: str = "") -> bool:
    """绑定UID"""
    try:
        async with get_session() as session:
            binding = await session.scalar(
                select(WwsBind).where(
                    WwsBind.user_id == user_id,
                    WwsBind.bot_id == bot_id
                )
            )
            if binding:
                binding.game_uid = uid
            else:
                session.add(WwsBind(
                    user_id=user_id,
                    bot_id=bot_id,
                    game_uid=uid,
                    group_id=group_id
                ))
            await session.commit()
        return True
    except Exception:
        return False

async def get_user_by_attr(user_id: str, bot_id: str, attr: str, value: str) -> WwsUser | None:
    """通过属性获取用户"""
    async with get_session() as session:
        if attr == "cookie":
            return await session.scalar(
                select(WwsUser).where(
                    WwsUser.user_id == user_id,
                    WwsUser.bot_id == bot_id,
                    WwsUser.cookie == value
                )
            )
        return None

async def create_or_update_user(user_id: str, bot_id: str, uid: str, cookie: str, did: str) -> WwsUser:
    """创建或更新用户"""
    async with get_session() as session:
        user = await session.scalar(
            select(WwsUser).where(
                WwsUser.user_id == user_id,
                WwsUser.bot_id == bot_id
            )
        )
        if user:
            user.uid = uid
            user.cookie = cookie
            user.did = did
        else:
            user = WwsUser(
                user_id=user_id,
                bot_id=bot_id,
                uid=uid,
                cookie=cookie,
                did=did
            )
            session.add(user)
        await session.commit()
        return user