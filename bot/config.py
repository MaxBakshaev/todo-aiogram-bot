import os
from dotenv import load_dotenv

load_dotenv()

# API URLs
API_URL = os.getenv("API_URL")
TASKS_URL = f"{API_URL}/tasks/"
CATEGORIES_URL = f"{API_URL}/categories/"

# Bot
BOT_TOKEN = os.getenv("TOKEN")

# Timezone
TIMEZONE = "America/Adak"

# Date format
DATE_INPUT_FORMAT = "%Y-%m-%d %H:%M"

# Skip keywords for categories
SKIP_KEYWORDS = {
    "-",
    "—",
    "пропустить",
    "skip",
    "none",
    "null",
    "нет",
    "без категории",
}

# Russian months
RU_MONTHS_GEN = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}
