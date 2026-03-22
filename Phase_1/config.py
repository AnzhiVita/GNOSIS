# config.py
# Список источников данных для ноды

SOURCES = [
    # Тип: txt — локальный текстовый файл
    {"type": "txt", "path": "https://lib.ru/NTL/KIBERNETIKA/IWANOW_W/odd_even.txt", "description": "Тестовый локальный файл"},

    # Тип: rss — научные и культурные ленты
    # Научные новости (NASA)
    {"type": "rss", "url": "https://www.nasa.gov/rss/dyn/breaking_news.rss", "description": "NASA Breaking News"},
    # Научно-популярный портал (Phys.org)
    {"type": "rss", "url": "https://phys.org/rss-feed/", "description": "Phys.org"},
    # Культурная лента (Би-би-си Культура) — часто доступна
    {"type": "rss", "url": "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "description": "BBC Arts & Entertainment"},
    # Альтернативная лента: новости науки и техники (Livescience)
    {"type": "rss", "url": "https://www.livescience.com/feeds/all", "description": "Live Science"},
    # Лента о природе и дикой природе (если доступна)
    # {"type": "rss", "url": "https://www.nationalgeographic.com/environment/feed/", "description": "National Geographic"},
]

# Интервал между циклами восприятия (в секундах)
SLEEP_INTERVAL = 600  # 10 минут

# Настройки для обработки текста
TEXT_CHUNK_SIZE = 500  # максимальная длина одного чанка (примерно абзац)