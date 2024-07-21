from flask import Flask, request, jsonify, abort
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

    full_transcript = download_full_transcript(video_id)
    comments = download_comments(video_id)

    summary = summarize_transcript(full_transcript)

    return jsonify({
        "summary": summary,
        # "tr": full_transcript
    })

# @app.errorhandler(500)
# def internal_server_error(e):
#     return jsonify(error=str(e)), 500


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
    comments = []

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append([comment['likeCount'], comment['textDisplay']])

    return comments

def summarize_transcript(transcript):
    response = AiClient.chat.completions.create(
        model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        max_tokens=512,
        temperature=0.2,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        messages=[{
            "role": "user",
            "content": '''
                Generate a summary for a YouTube video transcript. Important: Summary length must not exceed 15 words.

                You must respond ONLY with the JSON schema with the following structure. Do not add any additional comments. Don't make any greetings, like, "Here your response".

                You NEVER use " only '.

                Return me a valid json in this format:
                {
                    "summary": <Summary goes here>,
                }

                Here is the transcript:
            '''  + transcript
        }],
    )

    print(response.choices[0].message.content)

    data = json.loads(response.choices[0].message.content)

    return data



if __name__ == '__main__':
    app.run(debug=True)
