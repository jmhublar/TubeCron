# TubeCron

A cron-like system for processing YouTube transcripts and managing related tasks. It automatically creates Obsidian notes from your liked YouTube videos, including transcripts and AI-generated summaries.

## Features

- Fetches your liked YouTube videos
- Downloads video transcripts
- Generates summaries using either OpenAI or Ollama
- Creates formatted Obsidian notes with metadata, transcripts, and summaries
- Tracks processed videos to avoid duplicates
- Flexible LLM configuration with support for custom models

## Requirements

- Python 3.10 or higher
- One of the following:
  - OpenAI API key (set as OPENAI_API_KEY environment variable) for OpenAI service
  - Ollama running locally (or accessible via network) for Ollama service

## LLM Configuration

The system supports two LLM services for generating summaries:

### OpenAI (default)
```bash
# Use OpenAI with default model (gpt-3.5-turbo-16k)
python main.py --action process

# Use OpenAI with custom model
python main.py --action process --llm-service openai --llm-model gpt-4
```

### Ollama
```bash
# Use Ollama with default model (mistral)
python main.py --action process --llm-service ollama

# Use Ollama with custom model and host
python main.py --action process --llm-service ollama --llm-model llama2 --ollama-host http://localhost:11434
```

## Setup

1. Set up YouTube OAuth:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable the YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Download the client secrets file
   - Place it at `credentials/client_secret.json`

2. Configure Obsidian vault:
   - Notes are created in `~/Documents/Obsidian/YouTube/YouTube Videos` by default
   - The directory will be created automatically if it doesn't exist
   - Use `--vault-dir` to specify a different base directory

## Usage

Process new liked videos (default batch size of 10):
```bash
python main.py --action process
```

Process videos with custom batch size:
```bash
python main.py --action process --batch-size 5
```

List all liked videos:
```bash
python main.py --action liked_videos
```

Customize processing:
```bash
python main.py --action process --vault-dir /path/to/vault --batch-size 20
```

## Note Format

Each video creates a note with:
- YAML frontmatter with metadata
- Video title and link
- AI-generated summary
- Full transcript

## File Structure

```
.
├── credentials/           # YouTube OAuth credentials
│   └── client_secret.json
├── tokens/               # OAuth tokens
│   └── token.json
├── transcripts/          # Downloaded video transcripts
├── obsidian_vault/       # Generated Obsidian notes
│   └── YouTube Videos/
├── state.db             # SQLite database tracking processed videos
├── pyproject.toml       # Project configuration and dependencies
└── ...
