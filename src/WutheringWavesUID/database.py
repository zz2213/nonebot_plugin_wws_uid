from sqlalchemy import select
from nonebot_plugin_datastore import get_session
from .models import WwsBind

# 这些函数将用于替换 gsuid_core.utils.database.api 中的同功能函数
async def get_uid_by_qq(user_id: int) -> int | None:
    """[原生实现] 通过 QQ号 获取绑定的 UID"""
    async with get_session() as session:
        uid_str = await session.scalar(select(WwsBind.game_uid).where(WwsBind.user_id == str(user_id)))
        return int(uid_str) if uid_str else None

async def bind_uid_by_qq(user_id: int, uid: int) -> bool:
    """[原生实现] 通过 QQ号 绑定 UID"""
    try:
        async with get_session() as session:
            binding = await session.scalar(select(WwsBind).where(WwsBind.user_id == str(user_id)))
            if binding:
                binding.game_uid = str(uid)
            else:
                session.add(WwsBind(user_id=str(user_id), game_uid=str(uid)))
            await session.commit()
        return True
    except Exception:
        return False