# wws_native/models.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_datastore import get_base
Base = get_base()
class WwsBind(Base):
    __tablename__ = "wws_bind"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(32), index=True, unique=True)
    game_uid: Mapped[str] = mapped_column(String(32))