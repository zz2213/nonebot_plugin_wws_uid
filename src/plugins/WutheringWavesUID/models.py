# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/models.py

from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Text, Index
from .database import Base


class User(Base):
  """用户信息"""
  __tablename__ = "wuthering_waves_user"
  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(String(255), unique=True, index=True)
  user_token = Column(String(255))
  current_bind_uid = Column(String(255))


class UserBind(Base):
  """用户绑定的UID信息"""
  __tablename__ = "wuthering_waves_user_bind"
  id = Column(Integer, primary_key=True, index=True)
  user_id = Column(String(255), index=True)
  uid = Column(String(255), index=True)
  cookie = Column(Text)

  __table_args__ = (
    Index("ix_user_id_uid", "user_id", "uid"),
  )


class WavesGacha(Base):
  """抽卡记录 (迁移自 wutheringwaves_gachalog)"""
  __tablename__ = "waves_gacha"
  id = Column(Integer, primary_key=True, index=True, autoincrement=True)
  user_id = Column(String(255), index=True)
  uid = Column(String(255), index=True)
  gacha_type = Column(String(32), index=True)
  gacha_name = Column(String(255))
  item_id = Column(String(32), index=True)
  item_name = Column(String(255))
  item_type = Column(String(32))
  rarity = Column(Integer)
  time = Column(String(32))
  message_id = Column(String(255), unique=True, index=True)  # 使用 messageId 作为唯一键