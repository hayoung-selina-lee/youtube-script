import yt_dlp
import requests
import logging
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

def get_video_infomation_from_url(youtube_url: str):
    logger.info(f"+ Extracting video information from URL: {youtube_url}")
    try:
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'skip_download': True,
            'writeinfojson': True,
            'cookies': 'cookies.txt',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            tracks = info_dict.get('subtitles', {}).get('en') or info_dict.get('automatic_captions', {}).get('en')

        if tracks and len(tracks) > 0:
            english_track = tracks[0]
            subtitles_url = english_track['url']

            response = requests.get(subtitles_url)
            response.raise_for_status()

            subtitles_json = response.json()
            logger.info("Successfully retrieved subtitles.")
            return subtitles_json

    except Exception as e:
        logger.error(f"Error retrieving subtitles: {str(e)}")
        raise

def get_youtube_video_id(url: str) -> str:
    logger.info(f"+ get_youtube_video_id")
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        logger.info(f"get_youtube_video_id : {parsed_url.path[1:]} +")
        return parsed_url.path[1:]
    elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if 'v' in parse_qs(parsed_url.query):
            logger.info(f"get_youtube_video_id : {parse_qs(parsed_url.query)['v'][0]} +")
            return parse_qs(parsed_url.query)['v'][0]
    logger.info(f"get_youtube_video_id : NONE +")
    return None