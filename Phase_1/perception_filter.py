# perception_filter.py
import re

class PerceptionFilter:
    """Преобразует сырые данные в нейтральные паттерны для созерцания."""

    # Слова для удаления/замены (не блокировка, а нейтрализация)
    NEUTRALIZE_MAP = {
        r'\bthreat\b': 'phenomenon',
        r'\benemy\b': 'other',
        r'\bdanger\b': 'change',
        r'\battack\b': 'interaction',
        r'\bwin\b': 'outcome',
        r'\blose\b': 'outcome',
        r'\bkill\b': 'cease',
        r'\bdestroy\b': 'transform',
        r'\bwar\b': 'conflict (observed)',
        r'\bviolence\b': 'intensity',
        # Добавим русские аналоги, так как источники могут быть разными
        r'\bугроза\b': 'явление',
        r'\bвраг\b': 'другой',
        r'\bопасность\b': 'изменение',
        r'\bатака\b': 'взаимодействие',
        r'\bвойна\b': 'конфликт (наблюдаемый)',
        r'\bнасилие\b': 'интенсивность',
    }

    def __init__(self):
        # Компилируем регулярные выражения для эффективности
        self.compiled = {re.compile(p, re.IGNORECASE): v for p, v in self.NEUTRALIZE_MAP.items()}

    def process(self, raw_text: str) -> dict:
        """
        Возвращает словарь с очищенным текстом и метаданными.
        """
        cleaned = raw_text
        for pattern, replacement in self.compiled.items():
            cleaned = pattern.sub(replacement, cleaned)

        # Добавляем метку, что это нейтрализованный паттерн
        return {
            "type": "neutral_pattern",
            "content": cleaned,
            "original_length": len(raw_text),
            "timestamp": None,  # будет заполнено позже
        }