
import os
import yt_dlp
from rich import print
# FFmpeg installation directory
FFMPEG_DIR = (
    r"C:\Users\DRAGON-XOR\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.1-full_build\bin"
)

# Add FFmpeg to PATH so Pydub can find it
os.environ["PATH"] = (
    FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")
)

# Import Pydub after configuring PATH
from pydub import AudioSegment

# Configure Pydub explicitly
AudioSegment.converter = os.path.join(FFMPEG_DIR, "ffmpeg.exe")

# Download directory
DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:
    """
    Download audio from a YouTube URL and convert it to MP3.
    """

    if not url or not url.strip():
        raise ValueError("YouTube URL cannot be empty.")

    ffmpeg_exe = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
    ffprobe_exe = os.path.join(FFMPEG_DIR, "ffprobe.exe")

    if not os.path.isfile(ffmpeg_exe):
        raise FileNotFoundError("FFmpeg not found.")

    if not os.path.isfile(ffprobe_exe):
        raise FileNotFoundError("FFprobe not found.")

    output_template = os.path.join(
        DOWNLOAD_DIR, "%(id)s.%(ext)s"
    )

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "ffmpeg_location": FFMPEG_DIR,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            video_id = info["id"]

            audio_path = os.path.abspath(
                os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
            )

            if not os.path.isfile(audio_path):
                raise FileNotFoundError("MP3 file was not generated.")

            print("Audio downloaded successfully:", audio_path)

            return audio_path

    except Exception as e:
        raise RuntimeError(
            f"YouTube audio download failed: {e}"
        ) from e


def convert_to_wav(input_path: str) -> str:
    """
    Convert audio/video file to mono 16 kHz WAV format.
    """

    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = (
        os.path.splitext(input_path)[0] + "_converted.wav"
    )

    try:
        audio = AudioSegment.from_file(input_path)

        # Mono audio, 16 kHz sample rate
        audio = audio.set_channels(1).set_frame_rate(16000)

        audio.export(output_path, format="wav")

        print("WAV conversion successful:", output_path)

        return output_path

    except Exception as e:
        raise RuntimeError(
            f"Audio conversion failed: {e}"
        ) from e

def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list[str]:
    """
    Split WAV audio into smaller chunks.

    Args:
        wav_path: Input WAV file path.
        chunk_minutes: Duration of each chunk in minutes.

    Returns:
        List of paths of generated audio chunks.
    """

    if not os.path.isfile(wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    if chunk_minutes <= 0:
        raise ValueError("Chunk duration must be positive.")

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    # Get filename without extension
    base_path = os.path.splitext(wav_path)[0]

    for i, start in enumerate(range(0, len(audio), chunk_ms)):

        chunk = audio[start:start + chunk_ms]

        chunk_path = f"{base_path}_chunk_{i}.wav"

        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)

        print(f"Chunk {i + 1} saved: {chunk_path}")

    return chunks



def process_input(url: str, chunk_minutes: int = 10) -> list[str]:
    """
    Complete audio processing pipeline:
    YouTube URL -> MP3 -> WAV -> Audio Chunks.

    Args:
        url: YouTube video URL.
        chunk_minutes: Duration of each audio chunk in minutes.

    Returns:
        List of paths to generated WAV chunks.
    """

    try:
        print("\n[bold cyan]Step 1: Downloading YouTube audio...[/bold cyan]")

        mp3_path = download_youtube_audio(url)

        print(f"[green]MP3 downloaded: {mp3_path}[/green]")

        print("\n[bold cyan]Step 2: Converting audio to WAV...[/bold cyan]")

        wav_path = convert_to_wav(mp3_path)

        print(f"[green]WAV created: {wav_path}[/green]")

        print("\n[bold cyan]Step 3: Splitting audio into chunks...[/bold cyan]")

        chunks = chunk_audio(wav_path, chunk_minutes)

        print(f"\n[bold green]Processing completed![/bold green]")
        print(f"Total chunks generated: {len(chunks)}")

        return chunks

    except Exception as e:
        raise RuntimeError(f"Input processing failed: {e}") from e



if __name__ == "__main__":

    youtube_url = (
        "https://www.youtube.com/watch?v=_g2CgoTcVME"
    )

    try:
        process_input(youtube_url)

    except Exception as e:
        print("Error:", e)
