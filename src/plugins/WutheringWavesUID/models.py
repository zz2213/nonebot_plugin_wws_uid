from sqlalchemy import String, Text, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from nonebot_plugin_datastore import get_base

Base = get_base()

class WavesUser(Base):
    """鸣潮用户表"""
    __tablename__ = "waves_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), index=True)
    bot_id: Mapped[str] = mapped_column(String(32))
    uid: Mapped[str] = mapped_column(String(32))
    cookie: Mapped[str] = mapped_column(Text)
    did: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

class WavesBind(Base):
    """用户绑定表"""
    __tablename__ = "waves_binds"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), index=True)
    bot_id: Mapped[str] = mapped_column(String(32))
    game_uid: Mapped[str] = mapped_column(String(32))
    group_id: Mapped[str] = mapped_column(String(32), default="")
    is_main: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

class WavesCache(Base):
    """数据缓存表"""
    __tablename__ = "waves_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    value: Mapped[str] = mapped_column(Text)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)