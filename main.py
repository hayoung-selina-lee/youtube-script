from fastapi import FastAPI
from services import subtitles, cookies, download, transcribe, openai_utils, video_info
import logging
import sys

app = FastAPI()

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[MIMOS][%(levelname)s] %(message)s       (%(asctime)s)')

@app.get("/")
def root():
    return {"message": "Hello World"}

# getting subtitles without download like running service
@app.get("/script6/")
async def get_script_from_url_with_google_storage(youtubeURL: str):
    words_and_timing = subtitles.get_subtitles(youtubeURL)
    final_sentence_and_timing = openai_utils.run_openai_for_making_sentence(words_and_timing)

    return {
        "words_and_timing" : words_and_timing,
        "final_sentence_and_timing" : final_sentence_and_timing,
    }

# getting cookies first
@app.get("/script5/")
async def get_script_from_url_with_google_storage(youtubeURL: str):
    cookie_file_path = await cookies.get_cookies_from_url(youtubeURL)
    file_name = download.download_audio_with_ytdlp_with_coockies(youtubeURL, cookie_file_path)
    words_and_timing = await transcribe.transcribe_audio_with_word_time_offsets(file_name)
    final_sentence_and_timing = openai_utils.run_openai_for_making_sentence(words_and_timing)

    return {
        "message": f"Audio downloaded and saved as {file_name}",
        "words_and_timing" : words_and_timing,
        "final_sentence_and_timing" : final_sentence_and_timing,
    }

# using google storage for saving video.
@app.get("/script4/")
async def get_script_from_url_with_google_storage(youtubeURL: str):
    filename = download.download_audio_with_ytdlp_with_google_storage(youtubeURL)
    words_and_timing = transcribe.transcribe_audio_with_word_time_offsets_with_google_storage(filename)
    final_sentence_and_timing = openai_utils.run_openai_for_making_sentence(words_and_timing)
    #formatted_json = remove_escape_word_and_restore_json_string(final_sentence_and_timing)

    return {
        "message": f"Audio downloaded and saved as {filename}",
        #"url": url,
        "words_and_timing" : words_and_timing,
        "final_sentence_and_timing" : final_sentence_and_timing,
        #"kor_sentence_and_timing" : kor_sentence_and_timing
    }

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
        "subtitles": subtitles,
        "final_sentence_and_timing": final_sentence_and_timing,
    }

# using yt-dlp with download
@app.get("/script/")
async def get_script_from_url(youtubeURL: str):
    file_name = download.download_audio_with_ytdlp(youtubeURL)
    words_and_timing = transcribe.transcribe_audio_with_word_time_offsets(file_name)
    final_sentence_and_timing = openai_utils.run_openai_for_making_sentence(words_and_timing)
    return {
        "file_name": file_name,
        "final_sentence_and_timing": final_sentence_and_timing,
    }
