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
    video_info = download_video_info(video_id)

    summary = process_transcript(full_transcript)
    comment_info = process_comments(comments)

    print(comment_info)



    return jsonify({
        "summary": summary,
        # "tr": full_transcript
    })

# @app.errorhandler(500)
# def internal_server_error(e):
#     return jsonify(error=str(e)), 500


# ================== Fetch data from YouTube ==================
def download_full_transcript(video_id):
    transcripts = YouTubeTranscriptApi.get_transcript(video_id)

    full_transcript = ''
    for transcript in transcripts:
        full_transcript += transcript['text'] + ' '

    return full_transcript


def download_comments(video_id):
    request = YoutubeClient.commentThreads().list(
        part = "snippet",
        order = "relevance",
        maxResults = 100,
        textFormat = "plainText",
        videoId = video_id
    )

    response = request.execute()
    comments = []

    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append([comment['likeCount'], comment['textDisplay']])

    return comments

def download_video_info(video_id):
    request = YoutubeClient.videos().list(
        part = "snippet,statistics",
        id = video_id
    )

    response = request.execute()

    return {
        "title": response['items'][0]['snippet']['title'],
        "view_count": response['items'][0]['statistics']['viewCount'],
        "like_count": response['items'][0]['statistics']['likeCount'],
    }

# =============================================================
# ======================= Process Data ========================

def process_transcript(transcript):
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
                Generate a summary for a YouTube video transcript. Important: Summary length must not exceed 15 words. Those symbols are not allowed in the summary text: ".

                You must respond ONLY with the JSON schema with the following structure. Do not add any additional comments. Don't make any greetings, like, "Here your response".

                Return me a valid json in this format:
                {
                    "summary": "<Summary goes here>",
                }

                Here is the transcript:
            ''' + transcript
        }],
    )

    print(response.choices[0].message.content)
    data = json.loads(response.choices[0].message.content)

    return data

def process_comments(comments):
    if len(comments) == 0:
        return {
            "comments_summary": "Not enough comments",
            "clickbait_mentions": 0
        }

    comments_text = ''
    for comment in comments:
        if len(comments_text) + len(comment[1]) < 7000:
            comments_text += "[likes_count: {count}]\n".format(count=comment[1])
            comments_text += comment[1] + '\n'

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
                I will provide you with a list of comments from a YouTube video. I will provide you comment likes amount and comment text.

                I want you to provide a summary of the most discussed things. Make sure to focus on most liked comments.

                I also want you to count amount mentions of 'clickbait' in a comments.

                I will provide comments in the following format:
                ```
                    [likes_count: number]
                    comment_text
                    [likes_count: number]
                    comment_text
                    ...
                ```

                Important: Summary length must not exceed 20 words. Those symbols are not allowed in the summary text: ".

                Do not add any additional comments. Don't make any greetings, like, "Here your response".

                You must respond ONLY with the JSON schema with the following structure.

                Return me a valid json in this format:
                {
                    "comments_summary": "<Summary goes here>",
                    "clickbait_mentions": <Clickbait count goes here>,
                }

                Here are the comments:
            ''' + comments_text
        }],
    )

    print ('comments')
    print(response.choices[0].message.content)
    data = json.loads(response.choices[0].message.content)

    return data
# =============================================================
# ======================== Calc score =========================


# =============================================================

if __name__ == '__main__':
    app.run(debug=True)
