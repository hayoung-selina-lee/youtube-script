from fastapi import FastAPI
from services import download, transcribe, openai_utils, video_info
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO, format='[MIMOS][%(levelname)s] %(message)s       (%(asctime)s)')

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/script2/")
async def get_script_from_url_without_download(youtubeURL: str):
    subtitles = video_info.get_video_infomation_from_url(youtubeURL)
    words_and_timing = transcribe.transcribe_audio_with_word_time_offsets_without_download(subtitles)
    final_sentence_and_timing = openai_utils.run_openai_for_making_sentence(words_and_timing)
    return {
        "final_sentence_and_timing": final_sentence_and_timing,
    }

@app.get("/script/")
async def get_script_from_url(youtubeURL: str):
    file_name = download.download_audio_with_ytdlp(youtubeURL)
    words_and_timing = transcribe.transcribe_audio_with_word_time_offsets(file_name)
    final_sentence_and_timing = openai_utils.run_openai_for_making_sentence(words_and_timing)
    return {
        "final_sentence_and_timing": final_sentence_and_timing,
    }
