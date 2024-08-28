from transformers import pipeline
import logging
from youtube_transcript_api import YouTubeTranscriptApi

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
