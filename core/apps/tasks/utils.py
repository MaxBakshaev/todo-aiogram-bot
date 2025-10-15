import hashlib
import time


def generate_content_based_id(name: str = "") -> str:
    """Генерирует ID на основе содержимого и времени."""

    timestamp = int(time.time() * 1_000_000)
    content_hash = hashlib.md5(f"{name}_{timestamp}".encode()).hexdigest()

    return content_hash[:16]
