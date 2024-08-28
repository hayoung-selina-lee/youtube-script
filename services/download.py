import yt_dlp
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

def download_audio_with_ytdlp(youtube_url: str) -> str:
    logger.info(f"+ Downloading video from URL: {youtube_url}")
    
    temp_dir = tempfile.gettempdir()

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
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        file_name = ydl.prepare_filename(info_dict).replace('.webm', '.wav')

    logger.info(f"Downloaded video as {file_name}")
    return file_name
