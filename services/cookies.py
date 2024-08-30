import httpx
import json
import logging
import re
import os
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

def sanitize_url(url: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]', '_', url)

async def get_cookies_from_url(url: str) -> Optional[Dict[str, str]]:
    logger.info(f"+ get cookies from url {url}")

    temp_dir = '/tmp'
    folder_name = sanitize_url(url)
    folder_path = os.path.join(temp_dir, folder_name)
    cookie_file_path = os.path.join(folder_path, 'cookies.txt')

    if not os.path.exists(folder_path):
        logger.info(f"create folder {folder_path}")
        os.makedirs(folder_path)
    else :
        logger.info(f"Already had folder {cookie_file_path}")
        return cookie_file_path


    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            cookies = client.cookies.jar
            cookie_dict = {cookie.name: cookie.value for cookie in cookies}
            with open(cookie_file_path, 'w') as f:
                json.dump(cookie_dict, f)
            logger.info("get cookies from url :: SUCCESS +")
            return cookie_file_path
        else:
            logger.info("get cookies from url :: FAIL +")
            return None
