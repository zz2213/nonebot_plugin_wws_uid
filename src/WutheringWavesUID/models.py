from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_datastore import get_base

Base = get_base()

class WwsBind(Base):
    """鸣潮UID绑定数据表模型"""
    __tablename__ = "wws_bind"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), index=True)
    bot_id: Mapped[str] = mapped_column(String(32))
    game_uid: Mapped[str] = mapped_column(String(32))
    group_id: Mapped[str] = mapped_column(String(32), default="")

class WwsUser(Base):
    """鸣潮用户数据表模型"""
    __tablename__ = "wws_user"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), index=True)
    bot_id: Mapped[str] = mapped_column(String(32))
    uid: Mapped[str] = mapped_column(String(32))
    cookie: Mapped[str] = mapped_column(Text)
    did: Mapped[str] = mapped_column(String(64))