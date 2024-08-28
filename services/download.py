import yt_dlp
import os
import logging
import io
from google.cloud import storage

logger = logging.getLogger(__name__)

def download_audio_with_ytdlp(youtube_url: str) -> str:
    logger.info(f"+ Downloading video from URL: {youtube_url}")

    temp_dir = '/tmp'

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'wav',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'cookies': 'cookies.txt',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        },
        'quiet': False,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        file_name = ydl.prepare_filename(info_dict).replace('.webm', '.wav')

        final_path = os.path.join(temp_dir, os.path.basename(file_name))
        os.rename(file_name, final_path)

    logger.info(f"Downloaded video as {file_name}")
    return file_name

BUCKET_NAME = 'youtube-audio-test-storage'
from services.storage_client import get_google_storage_client
def download_audio_with_ytdlp_with_google_storage(youtube_url: str) -> str:
    logger.info(f"+ download_audio_with_ytdlp_with_google_storage: {youtube_url}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': '/tmp/temp_audio.%(ext)s',  # Temporary file location
        'writeinfojson': False,
        'writethumbnail': False
    }

    # Download audio file to a temporary location
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    # Find the downloaded file in the temporary directory
    temp_filename = '/tmp/temp_audio.wav'
    
    # Read the file into memory
    with open(temp_filename, 'rb') as f:
        audio_buffer = io.BytesIO(f.read())

    # Upload to GCS
    storage_client = get_google_storage_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    file_name = 'audio.wav'
    audio_blob = bucket.blob(file_name)
    audio_blob.upload_from_file(audio_buffer, content_type='audio/wav')

    logger.info(f"File uploaded to GCS as {file_name}")
    return file_name