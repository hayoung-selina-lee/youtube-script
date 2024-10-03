from transformers import pipeline
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from google.cloud import storage
import io
import os
import tempfile

logger = logging.getLogger(__name__)

def transcribe_audio_with_word_time_offsets(audio_file_path):
    logger.info("+ Transcribing audio with word time offsets.")
    transcriber = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        return_timestamps=True
    )
    
    transcription = transcriber(audio_file_path)
    words_and_timing = ""

    for segment in transcription['chunks']:
        start_time = segment['timestamp'][0]
        end_time = segment['timestamp'][1]
        text = segment['text']
        
        words_and_timing += f"Word: {text}, Start: {start_time}s, End: {end_time}s / "

    words_and_timing = words_and_timing.rstrip(" / ")
    logger.info("Transcribed audio successfully.")
    return words_and_timing

def transcribe_audio_with_word_time_offsets_without_download(subtitles):
    logger.info("+ Transcribing subtitles with word time offsets.")
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

    result_sentence = result_sentence.rstrip(" / ")
    logger.info("Transcribed subtitles successfully +")
    return result_sentence

def transcribe_audio_with_word_time_offsets_using_google_api(video_id: str) -> str:
    logger.info("+ transcribe_audio_with_word_time_offsets_using_google_api")
    try:
        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format the transcript into a single string
        transcript_text = ""
        
        # Iterate through the transcript entries
        for i, entry in enumerate(transcript):
            start_time = entry['start']
            text = entry['text']
            
            # Compute end time
            if i + 1 < len(transcript):
                end_time = transcript[i + 1]['start']
            else:
                end_time = start_time + entry['duration']
            
            transcript_text += f"Word: {text}, Start: {start_time}s, End: {end_time}s / "

        logger.info("transcribe_audio_with_word_time_offsets_using_google_api +")
        return transcript_text.rstrip(" / ")
    except Exception as e:
        return f"Error fetching transcript: {e}"

BUCKET_NAME = 'youtube-audio-test-storage'
from services.storage_client import get_google_storage_client
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
    storage_client = get_google_storage_client()
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