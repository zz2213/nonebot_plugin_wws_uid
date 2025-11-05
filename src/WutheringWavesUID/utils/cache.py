import time
from typing import Any, Dict


class TimedCache:
  """简单的超时缓存"""

  def __init__(self, timeout: int = 600, maxsize: int = 100):
    self.timeout = timeout
    self.maxsize = maxsize
    self._cache: Dict[str, Dict[str, Any]] = {}

  def get(self, key: str) -> Any:
    if key in self._cache:
      data = self._cache[key]
      if time.time() - data['timestamp'] < self.timeout:
        return data['value']
      else:
        del self._cache[key]
    return None

  def set(self, key: str, value: Any):
    if len(self._cache) >= self.maxsize:
      oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]['timestamp'])
      del self._cache[oldest_key]

    self._cache[key] = {
      'value': value,
      'timestamp': time.time()
    }

  def delete(self, key: str):
    if key in self._cache:
      del self._cache[key]