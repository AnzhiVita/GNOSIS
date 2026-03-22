# config.py
# Список источников данных для ноды

SOURCES = [
    # Тип: txt — локальный текстовый файл
    # {"type": "txt", "path": "sample_data.txt", "description": "Тестовый локальный файл"},

    # Тип: rss — научные и культурные ленты
    # Научные новости (NASA)
    {"type": "rss", "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss", "description": "NASA Breaking News"},
    # Научно-популярный портал (Phys.org)
    {"type": "rss", "url": "https://phys.org/rss-feed/", "description": "Phys.org"},
    {"type": "rss", "url": "http://rss.sciam.com/sciam/space", "description": "Scientific American Space"},
    {"type": "rss", "url": "https://www.nature.com/nature.rss", "description": "Nature"},
    # Альтернативная лента: новости науки и техники (Livescience)
    {"type": "rss", "url": "https://www.livescience.com/feeds/all", "description": "Live Science"},
     # Веб-источник — книга из библиотеки (текст будет скачан целиком и разбит)
    {"type": "web", "url": "https://lib.ru/GESSE/skazki.txt", "description": "Герман Гессе. Сказки, легенды, притчи (11 рассказов)"},
    {"type": "web", "url": "https://lib.ru/POECHIN/TZAOCHI/tzao_lyrics.txt", "description": "Цао Чжи — Стихотворения"},
]

# Интервал между циклами восприятия (в секундах)
SLEEP_INTERVAL = 600  # 10 минут

# Настройки для обработки текста
TEXT_CHUNK_SIZE = 2000  # максимальная длина одного чанка (примерно абзац)