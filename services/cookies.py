import httpx
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

async def get_cookies_from_url(url: str) -> Optional[Dict[str, str]]:
    async with httpx.AsyncClient() as client:
        logger.info("+ get cookies from url {url}")
        response = await client.get(url)
        if response.status_code == 200:
            logger.info("get cookies from url :: SUCCESS +")
            return client.cookies.jar
        logger.info("get cookies from url :: FAIL +")
        return None
