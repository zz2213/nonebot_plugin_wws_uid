# wws_native/core_logic/models.py
from pydantic import BaseModel
from typing import Optional

# [重构] 移除 tortoise 和 gsuid_core 依赖
# 这些类现在是纯粹的数据容器，用于类型注解

class UserData:
    """空实现，用于满足 import"""
    pass

class UserBind:
    """空实现，用于满足 import"""
    pass

# --- 移植自 WutheringWavesUID/utils/api/model.py ---
# 这是登录功能所必需的
class LoginResult(BaseModel):
    code: str
    uid: Optional[int] = None
    msg: str
    token: Optional[str] = None
    data: Optional[str] = None