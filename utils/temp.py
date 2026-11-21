import os
import subprocess

FFMPEG_DIR = r"C:\Users\DRAGON-XOR\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.1-full_build\bin"

subprocess.run([
    os.path.join(FFMPEG_DIR, "ffmpeg.exe"),
    "-version"
])