import asyncio
from enum import IntEnum
from typing import Any, Dict, Generic, Optional, TypeVar, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)

from gsuid_core.logger import logger

from ...utils.util import (
    generate_random_string,
    get_public_ip,
    send_master_info,
)

KURO_VERSION = "2.6.3"
PLATFORM_SOURCE = "ios"
CONTENT_TYPE = "application/x-www-form-urlencoded; charset=utf-8"


async def get_base_header(devCode: Optional[str] = None):
    header = {
        "source": PLATFORM_SOURCE,
        "Content-Type": CONTENT_TYPE,
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  KuroGameBox/2.6.3",
    }
    if devCode:
        header["devCode"] = devCode
    else:
        ip = await get_public_ip()
        header["devCode"] = (
            f"{ip}, Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)  KuroGameBox/2.6.3"
        )
    return header


async def get_community_header():
    devCode = generate_random_string()
    header = await get_base_header(devCode)
    header["source"] = "h5"
    header["version"] = KURO_VERSION
    return header


T = TypeVar("T")


class ThrowMsg(str):
    TOKEN_INVALID = "登录已过期，请重新登录"
    BAT_TOKEN_INVALID = "数据令牌已失效"
    DANGER_ENV = "当前环境存在风险无法进行操作，请切换网络环境后重试"
    SERVER_ERROR = "请求服务器失败，已达最大重试次数"
    SYSTEM_BUSY = "系统繁忙，请稍后再试"


class RespCode(IntEnum):
    ERROR = -999

    OK_ZERO = 0
    OK_HTTP = 200
    BAD_REQUEST = 400
    SERVER_ERROR = 500

    # 以下是kuro给的
    SERVER_EXTERNAL_ERROR = 102  # {'code': 102, 'msg': '服务器外部错误'} # 接口错误了
    CAPTCHA_ERROR = 130  # {'code': 130, 'msg': '验证码错误，请重新输入'}
    CAPTCHA_EXPIRED = 132  #  {'code': 132, 'msg': '验证码已经过期，请重新获取'}
    ROLE_QUERY_FAILED = 1000  # {'code': 1000, 'msg': '角色查询失败', 'data': None, 'success': False} 未知
    TOKEN_INVALID = 220  # {'code': 220, 'msg': '登录已过期，请重新登录'} token失效
    BAT_TOKEN_INVALID = 10903  # {'code': 10903, 'msg': '数据令牌已失效', 'data': None, 'success': False} bat失效
    DANGER_ENV = 270  # {'code': 270, 'msg': '当前环境存在风险无法进行操作，请切换网络环境后重试'} ip无了


# 发送主人信息
SEND_MASTER_INFO_CODES = (RespCode.DANGER_ENV.value,)
# 不发送主人信息
NOT_SEND_MASTER_INFO_CODES = (
    RespCode.ERROR.value,
    RespCode.OK_ZERO.value,
    RespCode.OK_HTTP.value,
    RespCode.TOKEN_INVALID.value,
    RespCode.BAT_TOKEN_INVALID.value,
    RespCode.CAPTCHA_ERROR.value,
    RespCode.CAPTCHA_EXPIRED.value,
    RespCode.ROLE_QUERY_FAILED.value,
)


def check_send_master_info(code: int, msg: str, data: Optional[T] = None) -> bool:
    if code in SEND_MASTER_INFO_CODES:
        return True

    if code in NOT_SEND_MASTER_INFO_CODES:
        return False

    logger.warning(f"[wwuid] code: {code} msg: {msg} data: {data}")
    return isinstance(msg, str) and msg != ""


class KuroApiResp(BaseModel, Generic[T]):
    model_config = ConfigDict(extra="ignore")

    code: int = Field(0, description="状态码")
    msg: str = Field("", description="消息")
    data: Optional[T] = Field(None, description="数据")

    @computed_field
    @property
    def success(self) -> bool:
        return self.code in (RespCode.OK_ZERO, RespCode.OK_HTTP)

    @classmethod
    def ok(
        cls,
        data: Optional[T] = None,
        msg: str = "请求成功",
        code: int = RespCode.OK_ZERO,
    ) -> "KuroApiResp[T]":
        return cls(code=code, msg=msg, data=data)

    @classmethod
    def err(cls, msg: str, code: int = RespCode.BAD_REQUEST) -> "KuroApiResp[T]":
        return cls(code=code, msg=msg, data=None)

    @property
    def is_token_invalid(self) -> bool:
        if self.code == RespCode.TOKEN_INVALID.value:
            return True
        return self.msg in ("重新登录", "登录已过期", "登录已过期，请重新登录")

    @property
    def is_bat_token_invalid(self) -> bool:
        if self.code == RespCode.BAT_TOKEN_INVALID.value:
            return True
        return self.msg in ("数据令牌已失效")

    @model_validator(mode="after")
    def _post_validate(self) -> "KuroApiResp[T]":
        if check_send_master_info(self.code, self.msg):
            try:
                asyncio.get_running_loop().create_task(send_master_info(self.msg))
            except RuntimeError:
                pass
        return self

    async def mark_cookie_invalid(self, uid: str, cookie: str):
        if not self.is_token_invalid:
            return
        from ...utils.database.models import WavesUser

        await WavesUser.mark_cookie_invalid(uid, cookie, "无效")

    def throw_msg(self) -> str:
        if isinstance(self.msg, str):
            return self.msg
        return ThrowMsg.SYSTEM_BUSY


if __name__ == "__main__":
    res = KuroApiResp[dict].ok({"uid": 12345})
    assert res.success
    print(res.model_dump_json())

    v = KuroApiResp.model_validate(res)
    print(v)

    p = {"code": -1, "data": "请求服务器失败，已达最大重试次数"}
    v = KuroApiResp.model_validate(p)
    print(v)

    p = {"code": -1, "data": "登录已过期", "msg": "登录已过期，请重新登录"}
    v = KuroApiResp[Union[str, Dict[str, Any]]].model_validate(p)
    print(v)
