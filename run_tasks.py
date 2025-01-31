#!/usr/bin/env python3
import os
import json
import argparse

from youtube_oauth_lib import YouTubeAuth
import db_state

def fetch_liked_videos(service, max_results=50):
    videos = []
    page_token = None
    while True:
        req = service.videos().list(
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

def like_and_post_one(service, db_path="state.db"):
    db_state.init_db(db_path)
    videos = fetch_liked_videos(service)

    for v in videos:
        video_id = v["id"]
        title = v["snippet"]["title"]

        if not db_state.is_posted(video_id, db_path):
            # "Post" it to stdout
            print(f"Posting one new liked video:\n- ID: {video_id}\n- Title: {title}\n")
            db_state.mark_posted(video_id, title, db_path)
            break
    else:
        print("No new liked videos to post.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        choices=["like_and_post", "liked_videos"],
        default="like_and_post",
        help="What action to perform."
    )
    args = parser.parse_args()

    creds_path = os.path.join("credentials", "client_secret.json")
    token_path = os.path.join("tokens", "token.json")

    yt_auth = YouTubeAuth(creds_path, token_path)
    service = yt_auth.get_authenticated_service()

    if args.action == "like_and_post":
        like_and_post_one(service)
    elif args.action == "liked_videos":
        # Example: list all liked videos
        data = fetch_liked_videos(service)
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
