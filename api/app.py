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

    summary_info = process_transcript(title=video_info['title'], transcript=full_transcript)
    comments_info = process_comments(comments)


    print(comments_info)





    return jsonify({
        "summary": summary_info['summary'],
        "clickbait_score": calc_clickbait_score(video_info, comments_info, summary_info, comments)
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

def process_transcript(transcript='', title=''):
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
                Generate a summary for a YouTube video transcript.

                I also want you to compare the video summary with the video title and provide me a similarity score from 0 to 100.

                Important: Summary length must not exceed 15 words. Those symbols are not allowed in the summary text: ".

                You must respond ONLY with the JSON schema with the following structure. Do not add any additional comments. Don't make any greetings, like, "Here your response".

                Return me a valid json in this format:
                {
                    "summary": "<Summary goes here>",
                    "title_similarity_score": "<Title similarity score goes here>",
                }

            ''' + "Video title: " + title + "\n\nHere is the transcript:" + transcript
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

def calc_clickbait_score(video_info=None, comments_info=None, summary_info=None, comments=None):
    if not video_info or not comments_info or not summary_info:
        raise Exception('Missing data')

    title_similarity_score = 100 - summary_info['title_similarity_score']
    likes_to_views_score = get_likes_to_views_clickbait_score(video_info)
    comments_score = get_comments_score(comments, comments_info)

    print('likes_to_views_score', likes_to_views_score)
    print('comments_score', comments_score)
    print('title_similarity_score', title_similarity_score)

    return 0.3 * likes_to_views_score + 0.3 * comments_score + 0.4 * title_similarity_score

def get_likes_to_views_clickbait_score(video_info):
    likes_to_views = int(video_info['like_count']) / int(video_info['view_count'])

    if likes_to_views < 0.01:
        return 100
    elif likes_to_views < 0.02:
        return 50

    return 0

def get_comments_score(comments, comments_info):
    clickbait_mentions_on_comment = comments_info['clickbait_mentions'] / len(comments)

    if clickbait_mentions_on_comment > 0.4:
        return 100
    elif clickbait_mentions_on_comment > 0.3:
        return 80
    elif clickbait_mentions_on_comment > 0.2:
        return 50
    elif clickbait_mentions_on_comment > 0.1:
        return 30
    elif clickbait_mentions_on_comment > 0.05:
        return 15

    return 0

# =============================================================

if __name__ == '__main__':
    app.run(debug=True)
