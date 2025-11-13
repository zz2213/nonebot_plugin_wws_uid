# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/alias_service.py

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import aiofiles

# 定义数据文件的根路径
# __file__ -> .../services/alias_service.py
# .parent -> .../services/
# .parent.parent -> .../WutheringWavesUID/
DATA_PATH = Path(__file__).parent.parent / "core" / "data" / "alias"

# 确保 alias 目录存在
DATA_PATH.mkdir(parents=True, exist_ok=True)

# 定义各个 JSON 文件的路径
CHAR_ALIAS_PATH = DATA_PATH / "char_alias.json"
WEAPON_ALIAS_PATH = DATA_PATH / "weapon_alias.json"
ECHO_ALIAS_PATH = DATA_PATH / "echo_alias.json"
SONATA_ALIAS_PATH = DATA_PATH / "sonata_alias.json"


class AliasService:
  """
  别名服务，用于异步、安全地读写别名 JSON 文件。
  (迁移自 wutheringwaves_alias/char_alias_ops.py 并进行了异步化改造)
  """

  def __init__(self):
    # 为每个文件创建一个锁，防止并发读写冲突
    self._locks = {
      CHAR_ALIAS_PATH: asyncio.Lock(),
      WEAPON_ALIAS_PATH: asyncio.Lock(),
      ECHO_ALIAS_PATH: asyncio.Lock(),
      SONATA_ALIAS_PATH: asyncio.Lock(),
    }
    # 确保所有 JSON 文件都存在
    for path in self._locks.keys():
      if not path.exists():
        self._initialize_json(path)

  def _initialize_json(self, file_path: Path):
    """同步创建空的 JSON 文件"""
    try:
      with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({}, f)
    except IOError:
      pass  # 忽略启动时的写入错误

  async def _read_alias_file(self, file_path: Path) -> Dict[str, str]:
    """(私有) 异步读取别名文件"""
    if not file_path.exists():
      return {}
    lock = self._locks.get(file_path)
    if not lock:
      lock = asyncio.Lock()
      self._locks[file_path] = lock

    async with lock:
      try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
          content = await f.read()
          return json.loads(content)
      except (json.JSONDecodeError, FileNotFoundError):
        return {}

  async def _write_alias_file(self, file_path: Path, data: Dict[str, str]) -> bool:
    """(私有) 异步写入别名文件"""
    lock = self._locks.get(file_path)
    if not lock:
      lock = asyncio.Lock()
      self._locks[file_path] = lock

    async with lock:
      try:
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
          await f.write(json.dumps(data, ensure_ascii=False, indent=4))
        return True
      except IOError:
        return False

  async def _get_alias_list(self, file_path: Path) -> str:
    """(私有) 获取别名列表的文本"""
    data = await self._read_alias_file(file_path)
    if not data:
      return "当前没有任何别名。"

    # 将 { "别名": "标准名" } 转换格式
    inverted_data: Dict[str, List[str]] = {}
    for alias, standard_name in data.items():
      if standard_name not in inverted_data:
        inverted_data[standard_name] = []
      inverted_data[standard_name].append(alias)

    # 生成消息
    msg_lines = ["当前别名列表如下：", "「标准名」: [别名列表]"]
    msg_lines.extend(
        f"「{name}」: {', '.join(aliases)}"
        for name, aliases in sorted(inverted_data.items())
    )
    return "\n".join(msg_lines)

  async def _find_alias(self, file_path: Path, name: str) -> str:
    """(私有) 查找别名或标准名"""
    data = await self._read_alias_file(file_path)
    if not data:
      return f"「{name}」未找到别名，也无别名指向它。"

    # 检查 name 是否是别名
    if name in data:
      return f"别名「{name}」-> 标准名「{data[name]}」"

    # 检查 name 是否是标准名
    aliases = [alias for alias, std_name in data.items() if std_name == name]
    if aliases:
      return f"标准名「{name}」<- 别名: {', '.join(aliases)}"

    return f"「{name}」未找到别名，也无别名指向它。"

  async def _add_alias(self, file_path: Path, standard_name: str, alias: str) -> str:
    """(私有) 添加别名"""
    data = await self._read_alias_file(file_path)

    if alias in data:
      return f"添加失败：别名「{alias}」已存在，指向「{data[alias]}」。"

    data[alias] = standard_name
    if await self._write_alias_file(file_path, data):
      return f"添加成功：「{alias}」->「{standard_name}」"
    else:
      return "添加失败：写入文件时发生错误。"

  async def _del_alias(self, file_path: Path, alias: str) -> str:
    """(私有) 删除别名"""
    data = await self._read_alias_file(file_path)

    if alias not in data:
      return f"删除失败：别名「{alias}」不存在。"

    standard_name = data.pop(alias)
    if await self._write_alias_file(file_path, data):
      return f"删除成功：「{alias}」->「{standard_name}」"
    else:
      return "删除失败：写入文件时发生错误。"

  # --- 角色别名 ---
  async def get_char_alias_list(self) -> str:
    return await self._get_alias_list(CHAR_ALIAS_PATH)

  async def find_char_alias(self, name: str) -> str:
    return await self._find_alias(CHAR_ALIAS_PATH, name)

  async def add_char_alias(self, standard_name: str, alias: str) -> str:
    return await self._add_alias(CHAR_ALIAS_PATH, standard_name, alias)

  async def del_char_alias(self, alias: str) -> str:
    return await self._del_alias(CHAR_ALIAS_PATH, alias)

  # --- 武器别名 ---
  async def get_weapon_alias_list(self) -> str:
    return await self._get_alias_list(WEAPON_ALIAS_PATH)

  async def find_weapon_alias(self, name: str) -> str:
    return await self._find_alias(WEAPON_ALIAS_PATH, name)

  async def add_weapon_alias(self, standard_name: str, alias: str) -> str:
    return await self._add_alias(WEAPON_ALIAS_PATH, standard_name, alias)

  async def del_weapon_alias(self, alias: str) -> str:
    return await self._del_alias(WEAPON_ALIAS_PATH, alias)

  # --- 声骸别名 ---
  async def get_echo_alias_list(self) -> str:
    return await self._get_alias_list(ECHO_ALIAS_PATH)

  async def find_echo_alias(self, name: str) -> str:
    return await self._find_alias(ECHO_ALIAS_PATH, name)

  async def add_echo_alias(self, standard_name: str, alias: str) -> str:
    return await self._add_alias(ECHO_ALIAS_PATH, standard_name, alias)

  async def del_echo_alias(self, alias: str) -> str:
    return await self._del_alias(ECHO_ALIAS_PATH, alias)

  # --- 声骸套装别名 ---
  async def get_sonata_alias_list(self) -> str:
    return await self._get_alias_list(SONATA_ALIAS_PATH)

  async def find_sonata_alias(self, name: str) -> str:
    return await self._find_alias(SONATA_ALIAS_PATH, name)

  async def add_sonata_alias(self, standard_name: str, alias: str) -> str:
    return await self._add_alias(SONATA_ALIAS_PATH, standard_name, alias)

  async def del_sonata_alias(self, alias: str) -> str:
    return await self._del_alias(SONATA_ALIAS_PATH, alias)


# 创建一个全局唯一的服务实例，以便在 handler 中依赖注入
alias_service = AliasService()