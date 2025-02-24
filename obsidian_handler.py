#!/usr/bin/env python3
import os
from datetime import datetime

class ObsidianHandler:
    def __init__(self, vault_dir=None):
        if vault_dir is None:
            vault_dir = os.path.expanduser("~/Documents/Obsidian/YouTube")
        self.vault_dir = vault_dir
        self.videos_dir = os.path.join(vault_dir, "YouTube Videos")
        os.makedirs(self.videos_dir, exist_ok=True)

    def create_note(self, video_id, title, transcript_path, summary):
        """Create an Obsidian note for a video with its transcript and summary."""
        # Create a safe filename from title
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        note_filename = f"{safe_title}-{video_id}.md"
        note_path = os.path.join(self.videos_dir, note_filename)

        # Read transcript
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()

        # Format creation date
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create note content
        note_content = f"""---
title: "{title}"
video_id: {video_id}
url: https://www.youtube.com/watch?v={video_id}
created: {created_date}
tags: [youtube, video, transcript]
---

# {title}

## Summary

{summary}

## Video Link

[Watch on YouTube](https://www.youtube.com/watch?v={video_id})

## Transcript

```text
{transcript_text}
```
"""

        # Write note to file
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(note_content)

        return note_path
