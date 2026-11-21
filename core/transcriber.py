
import os
import json
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from sarvamai import SarvamAI
from rich import print

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_MODEL = "saaras:v4"

if not SARVAM_API_KEY:
    raise RuntimeError("SARVAM_API_KEY is missing from .env")

client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)


def transcribe_batch(
    audio_paths: list[str],
    mode: str = "transcribe",
    with_diarization: bool = True,
    num_speakers: int | None = None,
    keyterms: list[str] | None = None
) -> list[str]:
    """
    Transcribe multiple audio files using Sarvam Batch API.

    Supports:
        - transcribe: Original language transcript
        - translate: English translation
        - codemix: Hindi-English mixed transcript
        - verbatim: Word-for-word transcript
        - translit: Romanized transcript

    Maximum:
        - 2 hours per audio file
        - 20 files per job

    Returns:
        List of transcripts in input order.
    """

    if not audio_paths:
        raise ValueError("No audio files provided.")

    for path in audio_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Audio not found: {path}")

    if mode not in {
        "transcribe", "translate", "codemix",
        "verbatim", "translit"
    }:
        raise ValueError(f"Invalid transcription mode: {mode}")

    transcripts = []

    # Batch API allows a maximum of 20 files per job.
    batches = [
        audio_paths[i:i + 20]
        for i in range(0, len(audio_paths), 20)
    ]

    for batch_index, batch_paths in enumerate(batches):

        print(
            f"\n[bold cyan]Starting batch "
            f"{batch_index + 1}/{len(batches)}...[/bold cyan]"
        )

        job_params = {
            "model": SARVAM_MODEL,
            "mode": mode,
            "with_diarization": with_diarization
        }

        if num_speakers is not None:
            job_params["num_speakers"] = num_speakers

        if keyterms:
            job_params["keyterms"] = keyterms

        # Create batch job
        job = client.speech_to_text_job.create_job(
            **job_params
        )

        # Upload audio files
        job.upload_files(file_paths=batch_paths)

        print("[yellow]Audio files uploaded.[/yellow]")

        # Start processing
        job.start()

        print("[yellow]Waiting for Sarvam AI...[/yellow]")

        # Wait until processing finishes
        job.wait_until_complete(
            poll_interval=5,
            timeout=1800
        )

        # Check results
        file_results = job.get_file_results()

        successful = file_results["successful"]
        failed = file_results["failed"]

        print(f"[green]Successful: {len(successful)}[/green]")
        print(f"[red]Failed: {len(failed)}[/red]")

        if failed:
            for item in failed:
                print(
                    f"[red]Failed file: {item}[/red]"
                )

            raise RuntimeError(
                f"{len(failed)} audio files failed in batch."
            )

        # Download JSON output files
        with tempfile.TemporaryDirectory() as temp_dir:

            job.download_outputs(output_dir=temp_dir)

            output_files = list(
                Path(temp_dir).glob("*.json")
            )

            # Sort 0.json, 1.json, 2.json...
            output_files.sort(
                key=lambda p: (
                    int(p.stem)
                    if p.stem.isdigit()
                    else p.stem
                )
            )

            if len(output_files) != len(batch_paths):
                raise RuntimeError(
                    "Mismatch between uploaded files "
                    "and downloaded transcript files."
                )

            for output_file in output_files:

                with open(
                    output_file,
                    "r",
                    encoding="utf-8"
                ) as f:
                    result = json.load(f)

                transcript = result.get("transcript", "")

                transcripts.append(transcript)

    return transcripts


def transcribe_all(
    chunks: list[str],
    mode: str = "transcribe",
    with_diarization: bool = True,
    num_speakers: int | None = None
) -> str:
    """
    Transcribe all audio chunks and combine results.
    """

    print(
        f"\n[bold green]Using Sarvam AI - "
        f"{SARVAM_MODEL}[/bold green]"
    )

    transcripts = transcribe_batch(
        audio_paths=chunks,
        mode=mode,
        with_diarization=with_diarization,
        num_speakers=num_speakers
    )

    full_transcript = "\n\n".join(
        text for text in transcripts if text
    )

    print("\n[bold green]Transcription completed![/bold green]")

    return full_transcript
