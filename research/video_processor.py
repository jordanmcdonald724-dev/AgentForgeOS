import os
from moviepy.video.io.VideoFileClip import VideoFileClip
import yt_dlp
from google.cloud import speech

def download_youtube_video(url, output_dir):
    """Download a YouTube video using yt-dlp."""
    ydl_opts = {
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info_dict)

def extract_audio_from_video(video_path, audio_output_path):
    """Extract audio from a video file."""
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_output_path)
    clip.close()

def transcribe_audio(audio_path):
    """Transcribe audio using Google Speech-to-Text API."""
    client = speech.SpeechClient()
    with open(audio_path, 'rb') as audio_file:
        audio_content = audio_file.read()

    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    transcripts = []
    for result in response.results:
        transcripts.append(result.alternatives[0].transcript)

    return " ".join(transcripts)

def process_video(video_source, output_dir):
    """Process a video file or YouTube URL."""
    if video_source.startswith("http"):
        video_path = download_youtube_video(video_source, output_dir)
    else:
        video_path = video_source

    audio_output_path = os.path.join(output_dir, "audio.wav")
    extract_audio_from_video(video_path, audio_output_path)

    transcription = transcribe_audio(audio_output_path)
    return transcription