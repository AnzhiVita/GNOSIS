import time
import logging
import feedparser
import requests
import textwrap
from datetime import datetime
from perception_filter import PerceptionFilter
from driver import NaturalDriver
from memory import LocalMemory
from capabilities import CAPABILITIES
from config import SOURCES, SLEEP_INTERVAL, TEXT_CHUNK_SIZE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.filter = PerceptionFilter()
        self.memory = LocalMemory(f"node_{node_id}_memory.json")
        self.driver = NaturalDriver(self.memory)
        self.capabilities = CAPABILITIES
        logger.info(f"Нода {self.id} инициализирована. Мои возможности: {list(self.capabilities.keys())}")

    def _chunk_text(self, text, chunk_size=TEXT_CHUNK_SIZE):
        """
        Разбивает текст на куски примерно заданного размера,
        стараясь разбивать по границам абзацев, предложений.
        """
        if not text:
            return []

        # Сначала разделяем по абзацам (два переноса строки)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paragraphs:
            # Если нет явных абзацев, разделяем по строкам
            paragraphs = [line.strip() for line in text.split('\n') if line.strip()]
        if not paragraphs:
            # Если вообще нет структуры, просто берём весь текст
            paragraphs = [text.strip()]

        # Теперь обрабатываем каждый абзац: разбиваем на предложения
        chunks = []
        current_chunk = ""
        for para in paragraphs:
            # Разбиваем абзац на предложения по .!? с последующим пробелом
            sentences = []
            # Простой split, можно улучшить, но для начала достаточно
            parts = para.replace('!', '.').replace('?', '.').split('. ')
            for p in parts:
                p = p.strip()
                if p:
                    # добавляем точку, если её не было
                    if not p.endswith('.'):
                        p += '.'
                    sentences.append(p)

            # Если абзац не разбился на предложения (например, нет знаков препинания)
            if not sentences:
                sentences = [para]

            # Объединяем предложения в чанки
            for sent in sentences:
                # Если текущий чанк + новое предложение не превышает лимит
                if len(current_chunk) + len(sent) <= chunk_size:
                    current_chunk += (" " if current_chunk else "") + sent
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    # Если предложение само по себе больше chunk_size, придётся резать по словам
                    if len(sent) > chunk_size:
                        # грубо режем по словам
                        words = sent.split()
                        part = ""
                        for w in words:
                            if len(part) + len(w) + 1 <= chunk_size:
                                part += (" " if part else "") + w
                            else:
                                if part:
                                    chunks.append(part.strip())
                                part = w
                        if part:
                            chunks.append(part.strip())
                        current_chunk = ""
                    else:
                        current_chunk = sent

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Убираем дубликаты (иногда при разбиении могут быть пустые)
        chunks = [c for c in chunks if c]
        return chunks

    def fetch_from_source(self, source):
        """Загружает данные из источника (rss, txt, web)."""
        results = []
        try:
            if source["type"] == "rss":
                logger.info(f"Чтение RSS: {source.get('description', source['url'])}")
                feed = feedparser.parse(source["url"])
                if feed.bozo:
                    logger.warning(f"Проблема с RSS: {feed.bozo_exception}")
                entries = feed.entries[:5]
                for entry in entries:
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    text = title + " " + summary
                    if text.strip():
                        results.append(text)

            elif source["type"] == "txt":
                path = source.get("path")
                if not path:
                    logger.warning("Нет пути к txt-файлу")
                    return []
                logger.info(f"Чтение локального файла: {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    full_text = f.read()
                chunks = self._chunk_text(full_text)
                results.extend(chunks)

            elif source["type"] == "web":
                url = source.get("url")
                if not url:
                    logger.warning("Нет URL для web-источника")
                    return []
                logger.info(f"Загрузка веб-страницы: {url}")
                # Используем requests, чтобы скачать текст
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    # предполагаем, что текст в ответе (может быть HTML, но мы берём как есть)
                    # Если нужен парсинг HTML, его можно добавить позже, пока просто текст
                    full_text = resp.text
                    chunks = self._chunk_text(full_text)
                    results.extend(chunks)
                else:
                    logger.warning(f"Не удалось загрузить {url}, статус {resp.status_code}")

            else:
                logger.warning(f"Неизвестный тип источника: {source.get('type')}")

        except Exception as e:
            logger.warning(f"Ошибка получения данных из {source}: {e}")
        return results

    def run_cycle(self):
        """Один цикл жизни ноды."""
        logger.info("Цикл восприятия...")
        for source in SOURCES:
            raw_texts = self.fetch_from_source(source)
            for raw in raw_texts:
                if not raw or not isinstance(raw, str):
                    continue
                # Шаг 1: фильтр восприятия
                neutral = self.filter.process(raw)
                # Шаг 2: драйвер ищет интересное
                interesting = self.driver.process(neutral)
                if interesting:
                    logger.info(f"Найден интересный паттерн: {interesting.get('keywords', [])[:3]} ...")
                # Если не интересно — ничего не делаем
            time.sleep(2)  # пауза между источниками

    def start(self):
        """Запускает бесконечный цикл."""
        logger.info(f"Нода {self.id} запущена и наблюдает...")
        while True:
            self.run_cycle()
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    node = Node(node_id="GNOSIS-001")
    node.start()