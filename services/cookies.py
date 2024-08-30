import httpx
import json
import logging
import re
import os
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


async def get_cookies_from_url(url: str) -> Optional[Dict[str, str]]:
    logger.info(f"+ get cookies from url {url}")

    source_filename = 'cookies.txt'

    temp_dir = '/tmp'
    cookie_file_path = os.path.join(temp_dir, 'cookies.txt')

    if not os.path.exists(cookie_file_path):
        with open(cookie_file_path, 'w') as file:
            file.write("")

        try:
            with open(source_filename, 'r') as source_file:
                content = source_file.read()

            # 복사할 파일을 쓰기 모드로 열기
            with open(cookie_file_path, 'w') as destination_file:
                # 읽어온 내용을 복사할 파일에 쓰기
                destination_file.write(content)

        except FileNotFoundError:
            print(f"파일 '{source_filename}'을(를) 찾을 수 없습니다.")
        except IOError as e:
            print(f"파일 작업 중 오류 발생: {e}")

    logger.info(f"get cookies from url {url} +")
    print(f"get cookies from url {url} +")
    return cookie_file_path
