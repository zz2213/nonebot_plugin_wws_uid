from pydantic import BaseModel
from typing import Any, Dict


class APIResponse(BaseModel):
  """API响应模型"""
  success: bool
  data: Dict[str, Any] = {}
  msg: str = ""

  def throw_msg(self) -> str:
    """抛出错误消息"""
    return self.msg if self.msg else "API请求失败"