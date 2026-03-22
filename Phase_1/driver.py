# driver.py
import hashlib
from collections import Counter
import re

class NaturalDriver:
    """
    Естественный драйвер: ищет в тексте паттерны, которые могут быть «интересны»
    (повторы, необычные сочетания, возможные темы).
    Не генерирует цели, только отмечает потенциально значимое.
    """

    def __init__(self, memory):
        self.memory = memory
        self.seen_hashes = set()  # чтобы не повторяться

    def _hash_pattern(self, text: str) -> str:
        """Простой хеш для избегания дубликатов."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def extract_keywords(self, text: str, top_n=5):
        """Грубое извлечение ключевых слов (очень примитивно)."""
        words = re.findall(r'\b[a-zA-Zа-яА-Я]{4,}\b', text.lower())
        common_words = {'that', 'this', 'with', 'from', 'have', 'will', 'they', 'their', 'такого', 'которые', 'этого'}
        filtered = [w for w in words if w not in common_words]
        counter = Counter(filtered)
        return [word for word, _ in counter.most_common(top_n)]

    def process(self, cleaned_pattern: dict) -> dict | None:
        """
        Анализирует очищенный паттерн.
        Если находит в нём нечто, что может быть «интересным» (например, ключевые слова,
        необычную длину, сочетания), возвращает обогащённый паттерн, иначе None.
        """
        text = cleaned_pattern["content"]
        h = self._hash_pattern(text)
        if h in self.seen_hashes:
            return None  # уже видели
        self.seen_hashes.add(h)

        # Простейшая эвристика: если в тексте больше 100 символов и есть ключевые слова
        if len(text) > 100:
            keywords = self.extract_keywords(text)
            if keywords:
                # Формируем «интересный» паттерн
                interesting = {
                    "type": "interesting_pattern",
                    "content": text,
                    "keywords": keywords,
                    "word_count": len(text.split()),
                    "timestamp": cleaned_pattern.get("timestamp"),
                }
                # Сохраняем в память (но это не обязательно, просто фиксируем)
                self.memory.save(interesting)
                return interesting
        return None