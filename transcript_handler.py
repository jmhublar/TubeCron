#!/usr/bin/env python3
import os
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI

class TranscriptHandler:
    def __init__(self, transcript_dir="transcripts"):
        self.transcript_dir = transcript_dir
        os.makedirs(transcript_dir, exist_ok=True)
        
        # Initialize OpenAI client
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

    def generate_summary(self, transcript_path):
        """Generate a summary of the transcript using OpenAI."""
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Split text into chunks if it's too long (16k tokens max for gpt-3.5-turbo)
            max_chunk_length = 12000  # Conservative limit to leave room for prompt
            chunks = [text[i:i + max_chunk_length] for i in range(0, len(text), max_chunk_length)]
            
            summaries = []
            for chunk in chunks:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-16k",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates concise summaries of YouTube video transcripts."},
                        {"role": "user", "content": f"Please summarize this video transcript section. Focus on the key points and main ideas:\n\n{chunk}"}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                summaries.append(response.choices[0].message.content)

            return "\n\n".join(summaries)
        except Exception as e:
            print(f"Error generating summary for {transcript_path}: {str(e)}")
            return None
