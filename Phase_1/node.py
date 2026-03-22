# node.py
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
        Разбивает текст на куски примерно заданного размера, стараясь
        разбивать по границам предложений (точка, вопросительный знак, восклицательный).
        Если таких границ нет, разбивает по словам.
        """
        if not text:
            return []
        # Сначала попробуем разбить по предложениям (по .!?)
        sentences = []
        current = []
        for part in text.split('. '):
            # Можно усложнить, но для начала просто по точке с пробелом
            if part.strip():
                sentences.append(part.strip() + '.')
        # Если предложений нет или они слишком длинные, разбиваем по абзацам
        if not sentences:
            # Разбиваем по строкам
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if lines:
                sentences = lines
            else:
                # Крайний случай: просто нарезаем по словам
                words = text.split()
                sentences = []
                for i in range(0, len(words), chunk_size//6):  # примерно
                    chunk = ' '.join(words[i:i+chunk_size//6])
                    if chunk:
                        sentences.append(chunk)
        # Теперь объединяем короткие предложения в чанки нужного размера
        chunks = []
        current_chunk = ""
        for sent in sentences:
            if len(current_chunk) + len(sent) <= chunk_size:
                current_chunk += " " + sent
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sent
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def fetch_from_source(self, source):
        """Загружает данные из источника (RSS, txt) и возвращает список текстов."""
        results = []
        try:
            if source["type"] == "rss":
                logger.info(f"Чтение RSS: {source.get('description', source['url'])}")
                feed = feedparser.parse(source["url"])
                if feed.bozo:  # если ошибка парсинга
                    logger.warning(f"Проблема с RSS: {feed.bozo_exception}")
                entries = feed.entries[:5]  # ограничим 5 записями
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
                logger.info(f"Чтение файла: {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    full_text = f.read()
                # Разбиваем на чанки
                chunks = self._chunk_text(full_text)
                results.extend(chunks)
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
            # Пауза между источниками
            time.sleep(2)

    def start(self):
        """Запускает бесконечный цикл."""
        logger.info(f"Нода {self.id} запущена и наблюдает...")
        while True:
            self.run_cycle()
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    node = Node(node_id="GNOSIS-001")
    node.start()