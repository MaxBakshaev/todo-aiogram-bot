import requests
import aiohttp
from config import CATEGORIES_URL, SKIP_KEYWORDS


async def find_or_create_category_id(name: str | None) -> int | None:
    if not name or name.strip().lower() in SKIP_KEYWORDS:
        return None

    name = name.strip()

    try:
        response = requests.get(
            CATEGORIES_URL,
            params={"name": name},
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            items = data.get("results", []) if isinstance(data, dict) else data

            for item in items:
                if isinstance(item, dict) and item.get("name") == name:
                    return item.get("id")
    except Exception:
        pass

    async with aiohttp.ClientSession() as session:
        async with session.post(
            CATEGORIES_URL, json={"name": name}, timeout=10
        ) as response:
            if response.status in (200, 201):
                created = await response.json()
                return created.get("id")

    return None
