import json
import os
import base64
from google.cloud import storage
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)

def get_google_storage_client():
    logger.info("+ get_google_storage_client")

    # 우선 GOOGLE_APPLICATION_CREDENTIALS 환경 변수 확인
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if credentials_path:
        logger.info("Using GOOGLE_APPLICATION_CREDENTIALS environment variable.")
        try:
            client = storage.Client.from_service_account_json(credentials_path)
            logger.info("Google Cloud Storage client successfully created using file path.")
            return client
        except Exception as e:
            logger.error(f"Failed to create Google Cloud Storage client from file path: {e}")
            raise
    
    # GOOGLE_APPLICATION_CREDENTIALS가 없으면 GOOGLE_APPLICATION_CREDENTIALS_BASE64 사용
    credentials_base64 = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_BASE64')
    
    if not credentials_base64:
        logger.error("Neither GOOGLE_APPLICATION_CREDENTIALS nor GOOGLE_APPLICATION_CREDENTIALS_BASE64 environment variables are set.")
        raise RuntimeError("Neither GOOGLE_APPLICATION_CREDENTIALS nor GOOGLE_APPLICATION_CREDENTIALS_BASE64 environment variables are set.")

    try:
        credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
        credentials_dict = json.loads(credentials_json)
        client = storage.Client.from_service_account_info(credentials_dict)
        logger.info("Google Cloud Storage client successfully created using base64-encoded credentials.")
        return client
    except Exception as e:
        logger.error(f"Failed to create Google Cloud Storage client from base64-encoded credentials: {e}")
        raise