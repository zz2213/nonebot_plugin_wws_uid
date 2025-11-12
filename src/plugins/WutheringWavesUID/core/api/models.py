from pydantic import BaseModel
from typing import Any, Dict, Optional

class APIResponse(BaseModel):
    """API响应模型"""
    success: bool
    data: Dict[str, Any] = {}
    msg: str = ""

    def throw_msg(self) -> str:
        return self.msg if self.msg else "API请求失败"

class LoginResponse(APIResponse):
    """登录响应"""
    token: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None

class UserInfoResponse(APIResponse):
    """用户信息响应"""
    uid: Optional[str] = None
    nickname: Optional[str] = None
    level: Optional[int] = None