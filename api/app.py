from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from together import Together
from googleapiclient.discovery import build
import os
import json

load_dotenv()

AiClient = Together(api_key=os.getenv("TOGETHER_API_KEY"))
YoutubeClient = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))

app = Flask(__name__)

@app.route('/api/v1/thumbnail-summary', methods=['GET'])
def get_video_summary():
    video_id = request.args.get('video_id')

    video_id = '3N4m5k9GAW0'
    full_transcript = download_full_transcript(video_id)
    comments = download_comments(video_id)


    return jsonify({
        "summary": summary,
        # "tr": full_transcript
    })


def download_full_transcript(video_id):
    transcripts = YouTubeTranscriptApi.get_transcript(video_id)

    full_transcript = ''
    for transcript in transcripts:
        full_transcript += transcript['text'] + ' '

    return full_transcript


def download_comments(video_id):
    request = YoutubeClient.commentThreads().list(
        part= "snippet,replies",
        order= "relevance",
        maxResults= 100,
        textFormat= "plainText",
        videoId= video_id
    )

    response = request.execute()

    print(response['items'][0]['snippet']['topLevelComment']['snippet']['likeCount'])

    comments = []

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append([comment['likeCount'], comment['textDisplay']])


    return comments


if __name__ == '__main__':
    app.run(debug=True)
