# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/database.py

import asyncio
from typing import Optional  # 修复：新增导入
from nonebot.log import logger  # 修复：新增导入，用于记录错误

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from nonebot import get_driver
from nonebot_plugin_localstore import get_data_file

from sqlalchemy import select  # 修复：新增导入，用于构建查询

# --- 数据库设置 ---
# 使用 nonebot_plugin_localstore 来获取数据库文件的标准路径
db_file = get_data_file("WutheringWavesUID", "wws_uid_data.db")
DB_URL = f"sqlite+aiosqlite:///{db_file}"

# 创建 SQLAlchemy 引擎
engine = create_async_engine(DB_URL, future=True, echo=False)

# 异步 Session 工厂
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 关键：定义所有模型都将继承的 Base
Base = declarative_base()


async def init_db():
    """
    异步初始化数据库, 创建所有表格
    """
    # 导入所有模型，确保它们被 Base.metadata 发现
    from . import models  # 确保 models 被导入，但 models.py 内部导入 Base 不会引发循环引用
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --- 用户绑定操作函数 (修复：实现缺失的函数，并解决循环导入) ---

async def bind_user(
        user_id: str,
        bot_id: str,
        uid: str,
        group_id: str = ""
) -> bool:
    """异步绑定用户UID，并更新当前使用UID"""
    # 修复循环导入：在函数内导入模型
    from .models import User, UserBind

    try:
        async with async_session() as session:
            # 1. 确保 UserBind 记录存在（存储用户与UID的绑定关系和可能的Cookie）
            stmt_bind = select(UserBind).where(UserBind.user_id == user_id, UserBind.uid == uid)
            result_bind = await session.execute(stmt_bind)
            user_bind = result_bind.scalars().first()

            if not user_bind:
                user_bind = UserBind(user_id=user_id, uid=uid, cookie="")
                session.add(user_bind)

            # 2. 更新 User 记录的当前绑定UID
            stmt_user = select(User).where(User.user_id == user_id)
            result_user = await session.execute(stmt_user)
            user = result_user.scalars().first()

            if user:
                # 存在用户记录，更新当前绑定UID
                user.current_bind_uid = uid
            else:
                # 不存在用户记录，创建新记录
                user = User(user_id=user_id, current_bind_uid=uid, user_token="")
                session.add(user)

            await session.commit()
            return True
    except Exception as e:
        logger.error(f"数据库绑定用户失败: {e}")
        return False


async def get_uid_by_user(user_id: str, bot_id: str) -> Optional[str]:
    """异步获取用户当前绑定的UID"""
    # 修复循环导入：在函数内导入模型
    from .models import User

    try:
        async with async_session() as session:
            # 只查询 User 表的 current_bind_uid
            stmt = select(User.current_bind_uid).where(User.user_id == user_id)
            result = await session.execute(stmt)
            uid = result.scalar_one_or_none()
            return uid
    except Exception as e:
        logger.error(f"数据库查询用户UID失败: {e}")
        return None


# --- 缓存设置 (使用 Redis) ---
# 这是所有 Service 文件 (game_service, character_service 等) 所需的
# get_cache 和 set_cache。

try:
    import redis.asyncio as redis

    # from nonebot_plugin_wws_uid.src.plugins import plugin_config # 移除此行，Redis配置通过全局获取

    # 从全局配置读取 Redis 连接信息
    redis_host = getattr(get_driver().config, "redis_host", "localhost")
    redis_port = getattr(get_driver().config, "redis_port", 6379)
    redis_db = getattr(get_driver().config, "redis_database", 0)
    redis_password = getattr(get_driver().config, "redis_password", None)

    # 创建 Redis 连接池
    _redis_pool = redis.ConnectionPool(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        decode_responses=True  # 自动解码
    )
    _redis_client = redis.Redis(connection_pool=_redis_pool)
    _CACHE_PREFIX = "wws_uid:"


    async def get_cache(key: str) -> Optional[str]:
        """(Redis) 获取缓存"""
        try:
            return await _redis_client.get(f"{_CACHE_PREFIX}{key}")
        except Exception as e:
            logger.error(f"Redis get_cache failed: {e}")
            return None


    async def set_cache(key: str, value: str, expires_in: int):
        """(Redis) 设置缓存"""
        try:
            await _redis_client.setex(f"{_CACHE_PREFIX}{key}", expires_in, value)
        except Exception as e:
            logger.error(f"Redis set_cache failed: {e}")

except ImportError:
    logger.warning("Redis 未安装 (pip install redis[hiredis]), 缓存功能将不可用。")


    # 创建一个空的 get/set_cache，防止插件崩溃
    async def get_cache(key: str) -> Optional[str]:
        return None


    async def set_cache(key: str, value: str, expires_in: int):
        pass
except Exception as e:
    logger.error(f"初始化 Redis 缓存失败: {e}，缓存功能将不可用。")


    async def get_cache(key: str) -> Optional[str]:
        return None


    async def set_cache(key: str, value: str, expires_in: int):
        pass