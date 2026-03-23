import base64
import importlib
import os
import re
import subprocess
from typing import Any, Dict, Optional, Tuple

_YOUTUBE_RE = re.compile(r"(youtube\.com|youtu\.be)", re.IGNORECASE)


def _is_youtube_url(url: str) -> bool:
    return bool(_YOUTUBE_RE.search(url or ""))


def _parse_vtt(text: str) -> str:
    out: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.upper().startswith("WEBVTT"):
            continue
        if "-->" in line:
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if line.startswith("NOTE"):
            continue
        out.append(line)
    compact: list[str] = []
    last = ""
    for line in out:
        if line == last:
            continue
        compact.append(line)
        last = line
    return " ".join(compact).strip()


def _pick_caption_source(info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    candidates: list[Tuple[int, Dict[str, Any]]] = []
    subs = info.get("subtitles")
    auto = info.get("automatic_captions")
    for priority, container in [(0, subs), (1, auto)]:
        if not isinstance(container, dict):
            continue
        for lang_key, entries in container.items():
            if not isinstance(lang_key, str):
                continue
            if not (lang_key == "en" or lang_key.startswith("en-") or lang_key.startswith("en_")):
                continue
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                url = entry.get("url")
                ext = entry.get("ext")
                if isinstance(url, str) and url.strip():
                    score = priority * 10
                    if ext == "vtt":
                        score += 0
                    elif ext == "srt":
                        score += 1
                    else:
                        score += 5
                    candidates.append((score, entry))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def _fetch_text(url: str) -> str:
    httpx = importlib.import_module("httpx")
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.text


def fetch_youtube_transcript(url: str) -> Optional[str]:
    if not _is_youtube_url(url):
        return None
    yt_dlp = importlib.import_module("yt_dlp")
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    if not isinstance(info, dict):
        return None
    entry = _pick_caption_source(info)
    if not entry:
        return None
    cap_url = entry.get("url")
    ext = entry.get("ext")
    if not isinstance(cap_url, str) or not cap_url.strip():
        return None
    raw = _fetch_text(cap_url)
    if ext == "srt":
        raw = raw.replace("\r", "\n")
        raw = re.sub(r"\n\d+\n", "\n", raw)
        raw = re.sub(r"\n\d{2}:\d{2}:\d{2},\d{3}\s+-->\s+\d{2}:\d{2}:\d{2},\d{3}\n", "\n", raw)
        return " ".join([ln.strip() for ln in raw.splitlines() if ln.strip()]).strip()
    return _parse_vtt(raw)


def download_youtube_video(url, output_dir):
    yt_dlp = importlib.import_module("yt_dlp")
    ydl_opts = {
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info_dict)

def extract_audio_from_video(video_path, audio_output_path):
    """Extract audio from a video file."""
    try:
        VideoFileClip = importlib.import_module("moviepy.video.io.VideoFileClip").VideoFileClip
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_output_path)
        clip.close()
        return
    except Exception:
        pass

    ffmpeg = "ffmpeg"
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        audio_output_path,
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "Unable to extract audio. Install moviepy or ffmpeg. "
            f"ffmpeg stderr: {completed.stderr[:500]}"
        )

def _fal_transcribe_audio_bytes(audio_bytes: bytes, mime: str = "audio/wav") -> str:
    api_key = (os.environ.get("FAL_API_KEY") or os.environ.get("FAL_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("FAL_API_KEY not set")

    httpx = importlib.import_module("httpx")
    data_uri = f"data:{mime};base64,{base64.b64encode(audio_bytes).decode('ascii')}"
    payload: Dict[str, Any] = {
        "input": {
            "audio_url": data_uri,
            "task": "transcribe",
            "chunk_level": "none",
        }
    }
    model = (os.environ.get("FAL_TRANSCRIBE_MODEL") or "fal-ai/wizper").strip()
    url = f"https://fal.run/{model}"
    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}

    with httpx.Client(timeout=300.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        raw = resp.json()

    if isinstance(raw, dict):
        if isinstance(raw.get("text"), str) and raw.get("text"):
            return str(raw["text"])
        data = raw.get("data")
        if isinstance(data, dict) and isinstance(data.get("text"), str) and data.get("text"):
            return str(data["text"])
        output = raw.get("output")
        if isinstance(output, dict) and isinstance(output.get("text"), str) and output.get("text"):
            return str(output["text"])
    raise RuntimeError("fal transcription returned unexpected response")


def _google_transcribe_wav_bytes(audio_bytes: bytes) -> str:
    speech = importlib.import_module("google.cloud.speech")
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_bytes)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    transcripts = []
    for result in response.results:
        transcripts.append(result.alternatives[0].transcript)
    return " ".join(transcripts).strip()


def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()

    try:
        return _fal_transcribe_audio_bytes(audio_bytes, mime="audio/wav")
    except Exception:
        pass

    try:
        return _google_transcribe_wav_bytes(audio_bytes)
    except Exception as exc:
        raise RuntimeError(str(exc)) from exc

def process_video(video_source, output_dir):
    if isinstance(video_source, str) and video_source.startswith("http") and _is_youtube_url(video_source):
        try:
            transcript = fetch_youtube_transcript(video_source)
            if isinstance(transcript, str) and transcript.strip():
                return transcript
        except Exception:
            pass

    if video_source.startswith("http"):
        video_path = download_youtube_video(video_source, output_dir)
    else:
        video_path = video_source

    audio_output_path = os.path.join(output_dir, f"audio_{os.getpid()}.wav")
    extract_audio_from_video(video_path, audio_output_path)
    return transcribe_audio(audio_output_path)
