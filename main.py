#!/usr/bin/env python3
import os
import json
import argparse
from pathlib import Path

from youtube_oauth_lib import YouTubeAuth
import db_state
from transcript_handler import TranscriptHandler
from obsidian_handler import ObsidianHandler

class TubeCron:
    def __init__(
        self,
        vault_dir=None,
        db_path="state.db",
        llm_service="openai",
        llm_model=None,
        ollama_host="http://localhost:11434"
    ):
        self.vault_dir = vault_dir or "/Users/cognomen/vaults/corp/corp/tubecron"
        self.db_path = db_path
        
        # Ensure required directories exist
        os.makedirs("credentials", exist_ok=True)
        os.makedirs("tokens", exist_ok=True)
        
        # Initialize handlers
        self.transcript_handler = TranscriptHandler(
            service=llm_service,
            model=llm_model,
            ollama_host=ollama_host
        )
        self.obsidian_handler = ObsidianHandler(self.vault_dir)
        
        # Initialize database
        db_state.init_db(self.db_path)
        
        # Setup YouTube service
        creds_path = os.path.join("credentials", "client_secret.json")
        token_path = os.path.join("tokens", "token.json")
        
        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Please place your YouTube OAuth client secrets file at: {creds_path}")
            
        yt_auth = YouTubeAuth(creds_path, token_path)
        self.service = yt_auth.get_authenticated_service()

    def fetch_liked_videos(self, max_results=50):
        """Fetch liked videos from YouTube."""
        videos = []
        page_token = None
        while True:
            req = self.service.videos().list(
                part="snippet,contentDetails",
                myRating="like",
                maxResults=max_results,
                pageToken=page_token
            )
            resp = req.execute()
            videos.extend(resp.get("items", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return videos

    def process_videos(self, batch_size=10):
        """Process videos in batches: fetch transcripts, generate summaries, create Obsidian notes."""
        # First, check for any videos that need transcripts
        pending_transcripts = db_state.get_pending_transcripts(self.db_path)
        for video_id, title in pending_transcripts:
            print(f"Fetching transcript for: {title}")
            transcript_path = self.transcript_handler.fetch_transcript(video_id)
            if transcript_path:
                db_state.update_transcript_status(video_id, transcript_path, self.db_path)
                print(f"Transcript saved to: {transcript_path}")
        
        # Then, check for any transcripts that need summaries/notes
        pending_summaries = db_state.get_pending_summaries(self.db_path)
        for video_id, title, transcript_path in pending_summaries:
            print(f"Generating summary for: {title}")
            summary = self.transcript_handler.generate_summary(transcript_path)
            if summary:
                note_path = self.obsidian_handler.create_note(video_id, title, transcript_path, summary)
                db_state.update_obsidian_status(video_id, note_path, self.db_path)
                print(f"Obsidian note created at: {note_path}")
        
        # Finally, check for any new videos to process
        videos = self.fetch_liked_videos()
        processed_count = 0
        
        for v in videos:
            video_id = v["id"]
            title = v["snippet"]["title"]

            if not db_state.is_posted(video_id, self.db_path):
                print(f"Found new video:\n- ID: {video_id}\n- Title: {title}")
                db_state.mark_posted(video_id, title, self.db_path)
                processed_count += 1
                
                if processed_count >= batch_size:
                    print(f"Reached batch size limit of {batch_size} videos")
                    break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        choices=["process", "liked_videos"],
        default="process",
        help="What action to perform."
    )
    parser.add_argument(
        "--vault-dir",
        help="Path to Obsidian vault directory",
        default=os.path.expanduser("~/Documents/Obsidian/YouTube")
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of videos to process in one batch (default: 10)"
    )
    parser.add_argument(
        "--llm-service",
        choices=["openai", "ollama"],
        default="openai",
        help="Which LLM service to use for generating summaries (default: openai)"
    )
    parser.add_argument(
        "--llm-model",
        help="Model to use with the chosen LLM service (default: gpt-3.5-turbo-16k for OpenAI, mistral for Ollama)"
    )
    parser.add_argument(
        "--ollama-host",
        default="http://localhost:11434",
        help="Ollama API host URL (default: http://localhost:11434)"
    )
    args = parser.parse_args()

    try:
        tubecron = TubeCron(
            vault_dir=args.vault_dir,
            llm_service=args.llm_service,
            llm_model=args.llm_model,
            ollama_host=args.ollama_host
        )
        
        if args.action == "process":
            tubecron.process_videos(batch_size=args.batch_size)
        elif args.action == "liked_videos":
            # Example: list all liked videos
            data = tubecron.fetch_liked_videos()
            print(json.dumps(data, indent=2))
            
    except FileNotFoundError as e:
        print(str(e))
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
