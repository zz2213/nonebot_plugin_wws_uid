# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/database.py

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from nonebot import get_driver
from nonebot_plugin_localstore import get_data_file

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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# --- 缓存设置 (使用 Redis) ---
# 这是所有 Service 文件 (game_service, character_service 等) 所需的
# get_cache 和 set_cache。

try:
    import redis.asyncio as redis
    from .. import plugin_config

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
    from nonebot.log import logger

    logger.warning("Redis 未安装 (pip install redis[hiredis]), 缓存功能将不可用。")


    # 创建一个空的 get/set_cache，防止插件崩溃
    async def get_cache(key: str) -> Optional[str]:
        return None


    async def set_cache(key: str, value: str, expires_in: int):
        pass
except Exception as e:
    from nonebot.log import logger

    logger.error(f"初始化 Redis 缓存失败: {e}，缓存功能将不可用。")


    async def get_cache(key: str) -> Optional[str]:
        return None


    async def set_cache(key: str, value: str, expires_in: int):
        pass