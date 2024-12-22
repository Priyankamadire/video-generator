from openai import OpenAI
import os
import edge_tts
import json
import asyncio
import whisper_timestamped as whisper
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals
from bs4 import BeautifulSoup
import requests
import argparse

# Function to scrape article text from a URL
def scrape_article(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract text (modify based on the website structure)
    paragraphs = soup.find_all("p")
    article_text = " ".join([p.get_text() for p in paragraphs])
    return article_text

if __name__ == "__main__":
    # Modify the argument to accept URL
    parser = argparse.ArgumentParser(description="Generate a video from an article URL.")
    parser.add_argument("url", type=str, help="The URL of the article")

    args = parser.parse_args()
    ARTICLE_URL = args.url  # Now takes URL
    SAMPLE_FILE_NAME = "audio_tts.wav"
    VIDEO_SERVER = "pexel"

    # Step 1: Scrape the article text
    article_text = scrape_article(ARTICLE_URL)
    print("Article text extracted.")

    # Step 2: Use the article text to generate a script
    response = generate_script(article_text)
    print("Script generated:\n", response)

    # Step 3: Use the script to generate audio
    asyncio.run(generate_audio(response, SAMPLE_FILE_NAME))

    # Step 4: Generate timed captions from the audio
    timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
    print("Timed captions generated:\n", timed_captions)

    # Step 5: Generate search terms for video
    search_terms = getVideoSearchQueriesTimed(response, timed_captions)
    print("Search terms generated:\n", search_terms)

    # Step 6: Generate background video URLs
    background_video_urls = None
    if search_terms is not None:
        background_video_urls = generate_video_url(search_terms, VIDEO_SERVER)
        print("Background video URLs generated:\n", background_video_urls)
    else:
        print("No background video found.")

    # Step 7: Merge empty intervals if necessary
    background_video_urls = merge_empty_intervals(background_video_urls)

    # Step 8: Generate final video with audio, captions, and background video
    if background_video_urls is not None:
        video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
        print("Video generated:", video)
    else:
        print("No video generated.")
