from fastapi import FastAPI
import yt_dlp
import urllib.parse
from transformers import pipeline
import json

from openai import OpenAI

client = OpenAI()
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/script/")
async def get_script_from_url(youtubeURL: str):
    filename = download_audio_with_ytdlp(youtubeURL)
    #filename = "The REAL GENIUS of Steve Jobs.wav"
    words_and_timing = transcribe_audio_with_word_time_offsets(filename)
    final_sentence_and_timing = run_openai_for_making_sentence(words_and_timing)

    # remove escape word and restore json string
    cleaned_json_str = final_sentence_and_timing.replace("\\n", "\n").replace("\\\"", "\"")
    cleaned_json_str = cleaned_json_str.strip("\"```json\n").strip("```")

    # pharsing
    json_data = json.loads(cleaned_json_str)

    formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
    
    return {
        "message": f"Audio downloaded and saved as {filename}",
        #"url": url,
        #"words_and_timing" : words_and_timing,
        "final_sentence_and_timing" : final_sentence_and_timing,
        #"kor_sentence_and_timing" : kor_sentence_and_timing
    }

def sanitize_filename(url: str) -> str:
    """Sanitize URL to create a valid filename."""
    return urllib.parse.quote_plus(url)  # Replace unsafe characters

def download_audio_with_ytdlp(youtube_url: str) -> str:
    """Downloads audio from YouTube using yt-dlp and returns the filename."""
    sanitized_url = sanitize_filename(youtube_url)  # Sanitize URL for filename

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,  # Only keep the audio
        'audioformat': 'wav',  # Specify WAV format
        #'outtmpl': f'{sanitized_url}.%(ext)s',  # Save file as sanitized_url.wav
        'outtmpl': '%(title)s.%(ext)s',  # save file as title.wav
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=True)
        file_name = ydl.prepare_filename(info_dict).replace('.webm', '.wav')
    
    return file_name

def transcribe_audio_with_word_time_offsets(audio_file_path):
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
    
    return words_and_timing


def run_openai_for_making_sentence(script):          
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You're an english app maker, skilled in making setence very well using given words. You can give me sentences naturally"},
        {"role": "user", "content": "I will give you word and start, end for staring time and end time of the word. If the sentence's time is more than 10s, you should give me separate the sentence. Could you make some sentences with completed sentence and star timestamp, end timestamp and during time (end time - start time) without any other mention that you want to say? And could you translate the sentence to Korean with very naturally like born in Korea? ?For example, If you got (Word : I, Start : 0.00 seconds, End : 1 seconds / Word : need, Start : 1 seconds, End : 2 seconds / Word : to, Start : 2 seconds, End : 3 seconds / Word : work, Start : 3 seconds, End : 4 seconds / Word : hard, Start : 4 seconds, End : 5 seconds / Word : because, Start : 5 seconds, End : 5.5 seconds / Word : I'm, Start : 5.5 seconds, End : 6 seconds / Word : Elon Musk, Start : 6 seconds, End : 6.6 seconds / Word : Sorry, Start : 6.6 seconds, End : 6.8 seconds / Word : Just, Start : 6.8 seconds, End : 6.9 seconds / Word : a, Start : 6.9 seconds, End : 7 seconds / Word : kidding, Start : 7 seconds, End : 7.1 seconds.) Then, you should give with the json format (text : I need to work hard because I'm Elon Musk, start : 0.00 seconds, end : 6.6 seconds, dur : 6.6 seconds, kor: 나는 일론 머스크이기 떄문에, 일을 열심히 해야한다. / text : Just a kidding, start : 6.6 seconds, end : 7.1 seconds, dur: 0.5 seconds, kor: 농담이야.) below are the scripts." + script}
    ]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    )
    return completion.choices[0].message.content
    
def run_openai_for_translating_korean(script):          
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "당신은 유능한 번역가입니다. 한국어와 영어 모두 원어민 수준으로 유창하게 구사할 수 있으며, 높은 수준의 어휘력을 갖고 있습니다."},
        {"role": "user", "content": "I will give you few sentences, starting and ending time. Could you translate sentence that is between starting time and ending time to Korean without any other mention that you want to say? And could ou give me during time between start and end time? For example, if you get (Sentence: The greatest people are self-managing. Start: 0.0s, End : 1.72s), you should return (text: The greatest people are self-managing. start: 0.0s, end : 1.72s, dur : 1.72s, kor : 가장 위대한 사람들은 자기 관리를 합니다.). below are the scripts." + script}]
    )
    return completion.choices[0].message.content