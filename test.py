from utils.audio_processor import process_input
from core.transcriber import transcribe_all


youtube_url = (
        "https://www.youtube.com/watch?v=FDnipYZQWl8"
    )

chunks = process_input(youtube_url)
print(transcribe_all(chunks=chunks,mode="translate"))