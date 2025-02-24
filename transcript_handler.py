#!/usr/bin/env python3
import os
from youtube_transcript_api import YouTubeTranscriptApi
import httpx
from openai import OpenAI
from typing import Literal
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class TranscriptHandler:
    def __init__(
        self,
        transcript_dir="transcripts",
        service: Literal["openai", "ollama"] = "openai",
        model: str = None,
        ollama_host: str = "http://localhost:11434"
    ):
        self.transcript_dir = transcript_dir
        self.service = service
        self.ollama_host = ollama_host
        self.model = model or ("gpt-3.5-turbo-16k" if service == "openai" else "mistral")
        
        os.makedirs(transcript_dir, exist_ok=True)
        
        # Initialize OpenAI client if using OpenAI
        if service == "openai":
            self.client = OpenAI()  # Will automatically use OPENAI_API_KEY from environment

    def fetch_transcript(self, video_id):
        """Fetch transcript for a video and save it to a file."""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Combine transcript text
            full_text = " ".join([entry["text"] for entry in transcript])
            
            # Save to file
            transcript_path = os.path.join(self.transcript_dir, f"{video_id}.txt")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            return transcript_path
        except Exception as e:
            print(f"Error fetching transcript for {video_id}: {str(e)}")
            return None

    def _generate_summary_openai(self, chunk: str) -> str:
        """Generate summary using OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries of YouTube video transcripts."},
                {"role": "user", "content": f"Please summarize this video transcript section. Focus on the key points and main ideas:\n\n{chunk}"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _generate_summary_ollama(self, chunk: str) -> str:
        """Generate summary using Ollama API with retry logic."""
        print(f"Generating summary for chunk of length {len(chunk)}...")
        with httpx.Client() as client:
            response = client.post(
                f"{self.ollama_host}/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that creates concise summaries of YouTube video transcripts."},
                        {"role": "user", "content": f"Please summarize this video transcript section. Focus on the key points and main ideas:\n\n{chunk}"}
                    ],
                    "stream": False
                },
                timeout=300.0  # Increased timeout for larger models like deepseek
            )
            response.raise_for_status()
            result = response.json()
            return result["message"]["content"]

    def generate_summary(self, transcript_path):
        """Generate a summary of the transcript using either OpenAI or Ollama."""
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Split text into smaller chunks for better processing
            max_chunk_length = 6000  # Reduced chunk size for better reliability
            chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
            
            summaries = []
            for chunk in chunks:
                if self.service == "openai":
                    summary = self._generate_summary_openai(chunk)
                else:  # ollama
                    summary = self._generate_summary_ollama(chunk)
                summaries.append(summary)

            return "\n\n".join(summaries)
        except Exception as e:
            print(f"Error generating summary for {transcript_path}: {str(e)}")
            return None
