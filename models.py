from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from nonebot_plugin_datastore import get_base

Base = get_base()

class WwsBind(Base):
    """鸣潮UID绑定表"""
    __tablename__ = "wws_bind"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), index=True, unique=True) # 用户QQ号
    game_uid: Mapped[str] = mapped_column(String(32)) # 游戏UID

    def __repr__(self):
        return f"<WwsBind(user_id={self.user_id}, game_uid={self.game_uid})>"