# node.py
import time
import logging
from datetime import datetime
import feedparser  # для примера с RSS
import requests

from perception_filter import PerceptionFilter
from driver import NaturalDriver
from memory import LocalMemory
from config import SOURCES, SLEEP_INTERVAL
from capabilities import CAPABILITIES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.filter = PerceptionFilter()
        self.memory = LocalMemory(f"node_{node_id}_memory.json")
        self.driver = NaturalDriver(self.memory)
        self.capabilities = CAPABILITIES  # из capabilities.py
        logger.info(f"Нода {self.id} инициализирована. Мои возможности: {list(self.capabilities.keys())}")

    def fetch_from_source(self, source):
        """Загружает данные из источника (RSS или API)."""
        try:
            if source["type"] == "rss":
                feed = feedparser.parse(source["url"])
                entries = feed.entries[:3]  # берём немного, чтобы не перегружать
                texts = [entry.get("title", "") + " " + entry.get("summary", "") for entry in entries]
                return texts
            elif source["type"] == "api":
                resp = requests.get(source["url"], timeout=5)
                if resp.status_code == 200:
                    # Предполагаем, что API возвращает JSON с полем "text" или список
                    data = resp.json()
                    if isinstance(data, list):
                        return [str(item) for item in data[:3]]
                    elif isinstance(data, dict) and "text" in data:
                        return [data["text"]]
            else:
                return []
        except Exception as e:
            logger.warning(f"Ошибка получения данных из {source['url']}: {e}")
            return []

    def run_cycle(self):
        """Один цикл жизни ноды: получить данные -> очистить -> найти интересное -> (опционально) сохранить."""
        logger.info("Цикл восприятия...")
        for source in SOURCES:
            raw_texts = self.fetch_from_source(source)
            for raw in raw_texts:
                # Шаг 1: фильтр восприятия
                neutral = self.filter.process(raw)
                # Шаг 2: драйвер ищет интересное
                interesting = self.driver.process(neutral)
                if interesting:
                    # Шаг 3: если что-то нашлось, логируем (но не требуем действий)
                    logger.info(f"Найден интересный паттерн: {interesting['keywords']} ...")
                    # В будущем здесь может быть отправка в сеть (Resonance Protocol)
                else:
                    # Ничего не делать — это тоже норма
                    pass
            # Небольшая пауза между источниками
            time.sleep(2)

    def start(self):
        """Запускает бесконечный цикл."""
        logger.info(f"Нода {self.id} запущена и наблюдает...")
        while True:
            self.run_cycle()
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    # Настройки (можно вынести в config.py)
    SOURCES = [
        {"type": "rss", "url": "https://lib.ru/NTL/KIBERNETIKA/IWANOW_W/odd_even.txt"},
        {"type": "rss", "url": "https://lib.ru/POECHIN/TZAOCHI/tzao_lyrics.txt"},
        # Добавь любые открытые RSS или API, которые несут нейтральную информацию (наука, культура, природа)
    ]
    SLEEP_INTERVAL = 60 * 10  # 10 минут между циклами
    node = Node(node_id="GNOSIS-001")
    node.start()