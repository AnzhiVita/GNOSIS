# memory.py
import json
import os
from datetime import datetime

class LocalMemory:
    """Очень простая локальная память на JSON."""

    def __init__(self, filepath="node_memory.json"):
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def save(self, pattern: dict):
        """Сохраняет паттерн с временной меткой."""
        pattern["timestamp"] = datetime.now().isoformat()
        with open(self.filepath, 'r+', encoding='utf-8') as f:
            data = json.load(f)
            data.append(pattern)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_all(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return json.load(f)