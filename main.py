from fastapi import FastAPI
import yt_dlp
import urllib.parse
from transformers import pipeline
import json
import tempfile
import os
import logging
import requests
import re
from youtube_transcript_api import YouTubeTranscriptApi
from google.cloud import storage
import io

from openai import OpenAI

client = OpenAI()
app = FastAPI()

logging.basicConfig(level=logging.INFO, format='[MIMOS][%(levelname)s] %(message)s       (%(asctime)s)')
logger = logging.getLogger(__name__)

@app.get("/")
def root():
    return {"message": "Hello World"}

BUCKET_NAME = 'youtube-audio-test-storage'
storage_client = storage.Client()

@app.get("/script4")
async def get_script_from_url_with_google_storage(youtubeURL: str):
    filename = download_audio_with_ytdlp_with_google_storage(youtubeURL)
    words_and_timing = transcribe_audio_with_word_time_offsets_with_google_storage(filename)
    final_sentence_and_timing = run_openai_for_making_sentence(words_and_timing)
    #formatted_json = remove_escape_word_and_restore_json_string(final_sentence_and_timing)

    return {
        "message": f"Audio downloaded and saved as {filename}",
        #"url": url,
        #"words_and_timing" : words_and_timing,
        "final_sentence_and_timing" : final_sentence_and_timing,
        #"kor_sentence_and_timing" : kor_sentence_and_timing
    }



# @app.get("/script3")
# async def get_script_from_url_with_google(youtubeURL: str):
#     video_id = get_youtube_video_id(youtubeURL)
#     words_and_timing = transcribe_audio_with_word_time_offsets_using_google_api(video_id)
#     final_sentence_and_timing = run_openai_for_making_sentence(words_and_timing)
#     #formatted_json = remove_escape_word_and_restore_json_string(final_sentence_and_timing)

#     return {
#         #"url": url,
#         #"words_and_timing" : words_and_timing,
#         "final_sentence_and_timing" : final_sentence_and_timing,
#         #"formatted_json" : formatted_json,
#         #"kor_sentence_and_timing" : kor_sentence_and_timing
#     }


@app.get("/script/")
async def get_script_from_url_without_download(youtubeURL: str):
    subtitles = get_video_infomation_from_url(youtubeURL)
    words_and_timing = transcribe_audio_with_word_time_offsets_without_download(subtitles)
    final_sentence_and_timing = run_openai_for_making_sentence(words_and_timing)
    #formatted_json = remove_escape_word_and_restore_json_string(final_sentence_and_timing)
    return {
        #"url": url,
        #"words_and_timing" : words_and_timing,
        "final_sentence_and_timing" : final_sentence_and_timing,
        #"formatted_json" : formatted_json,
        #"kor_sentence_and_timing" : kor_sentence_and_timing
    }


@app.get("/script2/")
async def get_script_from_url(youtubeURL: str):
    filename = download_audio_with_ytdlp(youtubeURL)
    #filename = "The REAL GENIUS of Steve Jobs.wav"
    words_and_timing = transcribe_audio_with_word_time_offsets(filename)
    cleanup_file(filename)
    final_sentence_and_timing = run_openai_for_making_sentence(words_and_timing)
    #formatted_json = remove_escape_word_and_restore_json_string(final_sentence_and_timing)

    return {
        "message": f"Audio downloaded and saved as {filename}",
        #"url": url,
        #"words_and_timing" : words_and_timing,
        "final_sentence_and_timing" : final_sentence_and_timing,
        #"kor_sentence_and_timing" : kor_sentence_and_timing
    }

def remove_escape_word_and_restore_json_string(origin_data):
    cleaned_json_str = origin_data.replace("\\n", "\n").replace("\\\"", "\"")
    cleaned_json_str = cleaned_json_str.strip("\"```json\n").strip("```")

    # pharsing
    json_data = json.loads(cleaned_json_str)

    return json.dumps(json_data, indent=2, ensure_ascii=False)

def sanitize_filename(url: str) -> str:
    """Sanitize URL to create a valid filename."""
    return urllib.parse.quote_plus(url)  # Replace unsafe characters

def download_audio_with_ytdlp(youtube_url: str) -> str:
    logger.info(f"+ Downloading video from URL: {youtube_url}")

    """Downloads audio from YouTube using yt-dlp and returns the filename."""
    sanitized_url = sanitize_filename(youtube_url)  # Sanitize URL for filename

    temp_dir = tempfile.gettempdir()  # Get system temporary directory (e.g., /tmp)

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,  # Only keep the audio
        'audioformat': 'wav',  # Specify WAV format
        #'outtmpl': f'{sanitized_url}.%(ext)s',  # Save file as sanitized_url.wav
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),  # Save to temporary directory
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        #'cookiesfrombrowser': ('firefox','chrome','vivaldi', 'default', 'BASICTEXT', 'Meta'),
        #'verbose': True, # for checking yt-dlp logs
        'cookies': 'cookies.txt',
        #'no-cookies': True,
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        file_name = ydl.prepare_filename(info_dict).replace('.webm', '.wav')

    logger.info(f"Downloading video from URL +")
    return file_name

def download_audio_with_ytdlp_with_google_storage(youtube_url: str) -> str:
    logger.info(f"+ Downloading video from URL: {youtube_url}")
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
    bucket = storage_client.bucket(BUCKET_NAME)
    file_name = 'audio.wav'
    audio_blob = bucket.blob(file_name)
    audio_blob.upload_from_file(audio_buffer, content_type='audio/wav')

    logger.info(f"File uploaded to GCS as {file_name}")
    return file_name

def transcribe_audio_with_word_time_offsets(audio_file_path):
    logger.info("+ get words and time from audio file")
    # Load the Whisper model using the pipeline
    transcriber = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        return_timestamps=True
    )
    
    # Perform speech-to-text with timestamps
    transcription = transcriber(audio_file_path)
    
    # Initialize the result string
    words_and_timing = ""
    
    # Extract and display the text and timestamps
    for segment in transcription['chunks']:
        start_time = segment['timestamp'][0]
        end_time = segment['timestamp'][1]
        text = segment['text']
        
        words_and_timing += f"Word: {text}, Start: {start_time}s, End: {end_time}s / "

    # Remove the trailing slash and space
    words_and_timing = words_and_timing.rstrip(" / ")
    
    logger.info("get words and time from audio file +")
    return words_and_timing

def transcribe_audio_with_word_time_offsets_with_google_storage(audio_file_name):
    logger.info("+ get words and time from audio file")
    # Load the Whisper model using the pipeline
    transcriber = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        return_timestamps=True
    )
    # try:
    # GCS에서 파일 가져오기
        
    bucket = storage_client.bucket(BUCKET_NAME)
    audio_blob = bucket.blob(audio_file_name)
    
    # 파일을 메모리로 다운로드
    audio_buffer = io.BytesIO()
    audio_blob.download_to_file(audio_buffer)
    audio_buffer.seek(0)  # 버퍼를 처음으로 이동

    # Create a temporary file to save the audio data
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        temp_file.write(audio_buffer.getvalue())
        temp_file_path = temp_file.name

    # Load the Whisper model using the pipeline
    transcriber = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        return_timestamps=True
    )

    # 오디오 데이터를 Whisper 모델로 변환
    transcription = transcriber(temp_file_path)

    # 텍스트 및 타임스탬프 추출
    words_and_timing = ""
    for segment in transcription['chunks']:
        start_time = segment['timestamp'][0]
        end_time = segment['timestamp'][1]
        text = segment['text']
        words_and_timing += f"Word: {text}, Start: {start_time}s, End: {end_time}s / "

    # 마지막 슬래시와 공백 제거
    words_and_timing = words_and_timing.rstrip(" / ")

    # 임시 파일 삭제
    os.remove(temp_file_path)

    logger.info("get words and time from audio file +")
    return words_and_timing

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

def run_openai_for_making_sentence(script):       
    
    logger.info("+ get sentence from words")

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You're an english app maker, skilled in making setence very well using given words. You can give me sentences naturally"},
        {"role": "user", "content": "I will give you word and start, end for staring time and end time of the word. If the sentence's time is more than 10s, you should give me separate the sentence. Could you make some sentences with completed sentence and star timestamp, end timestamp and during time (end time - start time) without any other mention that you want to say? And could you translate the sentence to Korean with very naturally like born in Korea? ?For example, If you got (Word : I, Start : 0.00 seconds, End : 1 seconds / Word : need, Start : 1 seconds, End : 2 seconds / Word : to, Start : 2 seconds, End : 3 seconds / Word : work, Start : 3 seconds, End : 4 seconds / Word : hard, Start : 4 seconds, End : 5 seconds / Word : because, Start : 5 seconds, End : 5.5 seconds / Word : I'm, Start : 5.5 seconds, End : 6 seconds / Word : Elon Musk, Start : 6 seconds, End : 6.6 seconds / Word : Sorry, Start : 6.6 seconds, End : 6.8 seconds / Word : Just, Start : 6.8 seconds, End : 6.9 seconds / Word : a, Start : 6.9 seconds, End : 7 seconds / Word : kidding, Start : 7 seconds, End : 7.1 seconds.) Then, you should give with the json format (text : I need to work hard because I'm Elon Musk, start : 0.00 seconds, end : 6.6 seconds, dur : 6.6 seconds, kor: 나는 일론 머스크이기 떄문에, 일을 열심히 해야한다. / text : Just a kidding, start : 6.6 seconds, end : 7.1 seconds, dur: 0.5 seconds, kor: 농담이야.) below are the scripts." + script}
    ])

    logger.info("get sentence from words +")

    return completion.choices[0].message.content
    
def run_openai_for_translating_korean(script):          
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 유능한 번역가입니다. 한국어와 영어 모두 원어민 수준으로 유창하게 구사할 수 있으며, 높은 수준의 어휘력을 갖고 있습니다."},
        {"role": "user", "content": "I will give you few sentences, starting and ending time. Could you translate sentence that is between starting time and ending time to Korean without any other mention that you want to say? And could ou give me during time between start and end time? For example, if you get (Sentence: The greatest people are self-managing. Start: 0.0s, End : 1.72s), you should return (text: The greatest people are self-managing. start: 0.0s, end : 1.72s, dur : 1.72s, kor : 가장 위대한 사람들은 자기 관리를 합니다.). below are the scripts." + script}]
    )
    return completion.choices[0].message.content

def get_video_infomation_from_url(youtube_url: str):
    logger.info("+ get_video_infomation_from_url : {youtube_url}")
    try:
        # Extract video information using yt-dlp
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,  # Don't download entire playlists
            'skip_download': True,  # Skip downloading the video itself
            'writeinfojson': True,  # Write video metadata to a JSON file
            'cookies': 'cookies.txt',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=False)
            tracks = info_dict.get('subtitles', {}).get('en') or info_dict.get('automatic_captions', {}).get('en')

        if tracks and len(tracks) > 0:
            # Find the English track
            english_track = tracks[0]
            subtitles_url = english_track['url']

            # Fetch the subtitles JSON
            response = requests.get(subtitles_url)
            response.raise_for_status()

            # Parse the JSON content
            subtitles_json = response.json()
            logger.info("get_video_infomation_from_url +")
            return subtitles_json

    except Exception as e:
        print('Error downloading subtitles:', str(e))
        raise  # Re-raise the error to be handled by the caller

def transcribe_audio_with_word_time_offsets_without_download(subtitles):
    logger.info("+ transcribe_audio_with_word_time_offsets_without_download")
    events = subtitles.get("events", [])
    result_sentence = ""
    for event in events:
        tStartMs = event.get('tStartMs', 0)
        dDurationMs = event.get('dDurationMs', 0)
        segments = event.get('segs', [])

        for segment in segments:
            word = segment.get('utf8', '')
            tOffsetMs = segment.get('tOffsetMs', 0)
            start_time = (tStartMs + tOffsetMs) / 1000.0
            end_time = (start_time + dDurationMs) / 1000.0

            if word.strip():
                result_sentence += f"Word: {word}, Start: {start_time}s, End: {end_time}s / "

    logger.info("transcribe_audio_with_word_time_offsets_without_download +")
    return result_sentence.rstrip(" / ")

def cleanup_file(file_path):
    logger.info(f"+ remove downloaded file: {file_path}")

    if os.path.exists(file_path):
        logger.info("removing...")
        os.remove(file_path)

    logger.info("remove downloaded file + ")

# def get_youtube_video_id(url: str) -> str:
#     patterns = [
#         r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
#         r"youtu\.be/([a-zA-Z0-9_-]{11})",
#         r"youtube\.com/embed/([a-zA-Z0-9_-]{11})"
#     ]
    
#     for pattern in patterns:
#         match = re.search(pattern, url)
#         if match:
#             return match.group(1)
    
#     raise ValueError("Invalid YouTube URL")

# def transcribe_audio_with_word_time_offsets_using_google_api(video_id: str) -> str:
#     try:
#         # Fetch the transcript
#         transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
#         # Format the transcript into a single string
#         transcript_text = ""
        
#         # Iterate through the transcript entries
#         for i, entry in enumerate(transcript):
#             start_time = entry['start']
#             text = entry['text']
            
#             # Compute end time
#             if i + 1 < len(transcript):
#                 end_time = transcript[i + 1]['start']
#             else:
#                 end_time = start_time + entry['duration']
            
#             transcript_text += f"Word: {text}, Start: {start_time}s, End: {end_time}s / "
        
#         return transcript_text.rstrip(" / ")
#     except Exception as e:
#         return f"Error fetching transcript: {e}"