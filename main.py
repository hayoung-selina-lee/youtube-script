from fastapi import FastAPI
from services import download, transcribe, openai_utils, video_info
import logging
import sys

app = FastAPI()

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[MIMOS][%(levelname)s] %(message)s       (%(asctime)s)')

@app.get("/")
def root():
    return {"message": "Hello World"}

# using google api that enable to get youtube video's information.
@app.get("/script3/")
async def get_script_from_url_with_google(youtubeURL: str):
    video_id = video_info.get_youtube_video_id(youtubeURL)
    words_and_timing = transcribe.transcribe_audio_with_word_time_offsets_using_google_api(video_id)
    final_sentence_and_timing = openai_utils.run_openai_for_making_sentence(words_and_timing)
    return {
        "video_id": video_id,
        "words_and_timing": words_and_timing,
        "final_sentence_and_timing": final_sentence_and_timing,
    }

# using yt-dlp without download
@app.get("/script2/")
async def get_script_from_url_without_download(youtubeURL: str):
    subtitles = video_info.get_video_infomation_from_url(youtubeURL)
    words_and_timing = transcribe.transcribe_audio_with_word_time_offsets_without_download(subtitles)
    final_sentence_and_timing = openai_utils.run_openai_for_making_sentence(words_and_timing)
    return {
        "final_sentence_and_timing": final_sentence_and_timing,
    }

# using yt-dlp with download
@app.get("/script/")
async def get_script_from_url(youtubeURL: str):
    file_name = download.download_audio_with_ytdlp(youtubeURL)
    words_and_timing = transcribe.transcribe_audio_with_word_time_offsets(file_name)
    final_sentence_and_timing = openai_utils.run_openai_for_making_sentence(words_and_timing)
    return {
        "final_sentence_and_timing": final_sentence_and_timing,
    }
