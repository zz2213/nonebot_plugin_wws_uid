from sqlalchemy import select, update, delete
from nonebot_plugin_datastore import get_session
from .models import WavesUser, WavesBind, WavesCache
from datetime import datetime

# WavesUser 相关操作
async def get_user_by_user_id(user_id: str, bot_id: str) -> WavesUser | None:
    """通过用户ID获取用户"""
    async with get_session() as session:
        return await session.scalar(
            select(WavesUser).where(
                WavesUser.user_id == user_id,
                WavesUser.bot_id == bot_id
            )
        )

async def get_user_by_cookie(cookie: str) -> WavesUser | None:
    """通过Cookie获取用户"""
    async with get_session() as session:
        return await session.scalar(
            select(WavesUser).where(WavesUser.cookie == cookie)
        )

async def create_or_update_user(
    user_id: str,
    bot_id: str,
    uid: str,
    cookie: str,
    did: str
) -> WavesUser:
    """创建或更新用户"""
    async with get_session() as session:
        user = await session.scalar(
            select(WavesUser).where(
                WavesUser.user_id == user_id,
                WavesUser.bot_id == bot_id
            )
        )

        if user:
            user.uid = uid
            user.cookie = cookie
            user.did = did
            user.updated_at = datetime.now()
        else:
            user = WavesUser(
                user_id=user_id,
                bot_id=bot_id,
                uid=uid,
                cookie=cookie,
                did=did
            )
            session.add(user)

        await session.commit()
        return user

# WavesBind 相关操作
async def get_bind_by_user(user_id: str, bot_id: str) -> WavesBind | None:
    """获取用户绑定"""
    async with get_session() as session:
        return await session.scalar(
            select(WavesBind).where(
                WavesBind.user_id == user_id,
                WavesBind.bot_id == bot_id,
                WavesBind.is_main == True
            )
        )

async def bind_user(
    user_id: str,
    bot_id: str,
    game_uid: str,
    group_id: str = ""
) -> bool:
    """绑定用户UID"""
    try:
        async with get_session() as session:
            # 取消现有主绑定
            await session.execute(
                update(WavesBind)
                .where(
                    WavesBind.user_id == user_id,
                    WavesBind.bot_id == bot_id,
                    WavesBind.is_main == True
                )
                .values(is_main=False)
            )

            # 创建新绑定
            bind = WavesBind(
                user_id=user_id,
                bot_id=bot_id,
                game_uid=game_uid,
                group_id=group_id,
                is_main=True
            )
            session.add(bind)

            await session.commit()
            return True
    except Exception:
        return False

async def get_uid_by_user(user_id: str, bot_id: str) -> str | None:
    """通过用户ID获取UID"""
    bind = await get_bind_by_user(user_id, bot_id)
    return bind.game_uid if bind else None

# WavesCache 相关操作
async def get_cache(key: str) -> str | None:
    """获取缓存"""
    async with get_session() as session:
        cache = await session.scalar(
            select(WavesCache).where(
                WavesCache.key == key,
                WavesCache.expires_at > datetime.now()
            )
        )
        return cache.value if cache else None

async def set_cache(key: str, value: str, expires_in: int = 3600):
    """设置缓存"""
    async with get_session() as session:
        # 删除过期缓存
        await session.execute(
            delete(WavesCache).where(WavesCache.expires_at <= datetime.now())
        )

        # 更新或插入新缓存
        cache = await session.scalar(
            select(WavesCache).where(WavesCache.key == key)
        )

        expires_at = datetime.now().timestamp() + expires_in
        expires_at = datetime.fromtimestamp(expires_at)

        if cache:
            cache.value = value
            cache.expires_at = expires_at
        else:
            cache = WavesCache(
                key=key,
                value=value,
                expires_at=expires_at
            )
            session.add(cache)

        await session.commit()