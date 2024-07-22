from flask import Flask, request, jsonify, abort
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from together import Together
from googleapiclient.discovery import build
import os
import json
from flask_cors import CORS

load_dotenv()

AiClient = Together(api_key=os.getenv("TOGETHER_API_KEY"))
YoutubeClient = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/api/v1/thumbnail-summary", methods=["GET"])
def get_video_summary():
    video_id = request.args.get("video_id")

    full_transcript = download_full_transcript(video_id)
    comments = download_comments(video_id)
    video_info = download_video_info(video_id)

    print(">>>>starting processing")
    summary_info = process_transcript(
        title=video_info["title"], transcript=full_transcript
    )
    comments_info = process_comments(comments)
    print(">>>>processing is finished")

    clickbait = calc_clickbait_score(video_info, comments_info, summary_info, comments)

    return jsonify(
        {
            "clickbait_score": clickbait["score"],
            "justification": clickbait["justification"],
            "tldr_of_comments": comments_info["comments_summary"],
            "video_summary": summary_info["summary"],
            "video_id": video_id
        }
    )


# @app.errorhandler(500)
# def internal_server_error(e):
#     return jsonify(error=str(e)), 500


# ================== Fetch data from YouTube ==================
def download_full_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-UK'])

    except:
        try:
            transcript = download_translated_transcript(video_id)
        except Exception as e:
            print(e)
            abort(500, 'Failed to load transcript')

    full_transcript = ""
    for transcript in transcript:
        full_transcript += transcript["text"] + " "

    return full_transcript

def download_translated_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        language_code = list(transcript_list)[0].language_code
        transcript = transcript_list.find_transcript([language_code])
        return transcript.translate('en').fetch()
    except Exception as e:
        print(e)
        abort(500, 'Failed to load transcript')

def download_comments(video_id):
    try:
        request = YoutubeClient.commentThreads().list(
            part="snippet",
            order="relevance",
            maxResults=100,
            textFormat="plainText",
            videoId=video_id,
        )

        response = request.execute()
        comments = []

        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append([comment["likeCount"], comment["textDisplay"]])

        return comments

    except Exception as e:
        print(e)
        abort(500, 'Failed to load comments')


def download_video_info(video_id):
    try:
        request = YoutubeClient.videos().list(part="snippet,statistics", id=video_id)

        response = request.execute()

        return {
            "title": response["items"][0]["snippet"]["title"],
            "view_count": response["items"][0]["statistics"]["viewCount"],
            "like_count": response["items"][0]["statistics"]["likeCount"],
        }

    except Exception as e:
        print(e)
        abort(500, 'Failed to load video info')


# =============================================================
# ======================= Process Data ========================
def extract_json(content):
    start = content.find("{")
    end = content.rfind("}")

    return json.loads(content[start : end + 1])


def process_transcript(transcript="", title=""):
    # TODO: solve issue for longer videos
    if len(transcript) > 7800:
        transcript = transcript[0:7800]

    try:
        response = AiClient.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
            max_tokens=512,
            temperature=0.2,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            messages=[
                {
                    "role": "user",
                    "content": """
                        Generate a summary for a YouTube video transcript.

                        I also want you to compare the video summary with the video title and provide me a similarity score from 0 to 100.

                        Important: Summary length must not exceed 15 words. Those symbols are not allowed in the summary text: ".

                        You must respond ONLY with the JSON schema with the following structure. Do not add any additional comments. Don't make any greetings, like, "Here your response".

                        Return me a valid json in this format:
                        {
                            "summary": "<Summary goes here>",
                            "title_similarity_score": "<Title similarity score goes here>",
                        }

                    """
                    + "Video title: "
                    + title
                    + "\n\nHere is the transcript:"
                    + transcript,
                }
            ],
        )
        content = response.choices[0].message.content

        print(content)

        return extract_json(content)
    except Exception as e:
        print(e)
        abort(500, 'Failed to process transcript')


def process_comments(comments):
    if len(comments) == 0:
        return {"comments_summary": "Not enough comments", "clickbait_mentions": 0}

    comments_text = ""
    for comment in comments:
        if len(comments_text) + len(comment[1]) < 7000:
            comments_text += "[likes_count: {count}]\n".format(count=comment[1])
            comments_text += comment[1] + "\n"

    try:
        response = AiClient.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
            max_tokens=512,
            temperature=0.2,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            messages=[
                {
                    "role": "user",
                    "content": """
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
                    """
                    + comments_text,
                }
            ],
        )
        content = response.choices[0].message.content

        print(content)

        return extract_json(content)
    except Exception as e:
        print(e)
        abort(500, 'Failed to process comments')


# =============================================================
# ======================== Calc score =========================


def calc_clickbait_score(
    video_info=None, comments_info=None, summary_info=None, comments=None
):
    if not video_info or not comments_info or not summary_info:
        raise Exception("Missing data")

    title_similarity_score = 100 - summary_info["title_similarity_score"]
    likes_to_views_score = get_likes_to_views_clickbait_score(video_info)
    comments_score = get_comments_score(comments, comments_info)

    print("likes_to_views_score", likes_to_views_score)
    print("comments_score", comments_score)
    print("title_similarity_score", title_similarity_score)
    score = round(
        0.4 * likes_to_views_score
        + 0.3 * comments_score
        + 0.3 * title_similarity_score,
        1,
    )
    justification = get_justification(
        likes_to_views_score, comments_score, title_similarity_score
    )

    return {"score": score, "justification": justification}


def get_justification(
    likes_to_views_score=0, comments_score=0, title_similarity_score=0
):
    justification = ["The video has"]

    if likes_to_views_score > 50:
        justification.append(" a low like-to-view ratio")
    elif likes_to_views_score > 29:
        justification.append(" a medium like-to-view ratio")

    if comments_score > 50:
        justification.append(", a low like-to-view ratio")
    elif comments_score > 29:
        justification.append(", a medium like-to-view ratio")

    if title_similarity_score > 50:
        if len(justification) > 1:
            justification.append(", and has")
        justification.append(" a title that does not match the content")
    elif title_similarity_score > 29:
        if len(justification) > 1:
            justification.append(", and has")
        justification.append(" a title that partially match the content")

    if len(justification) > 1:
        justification.append(".")
    else:
        justification.append(" a low clickbait score.")

    return "".join(justification)


def get_likes_to_views_clickbait_score(video_info):
    likes_to_views = int(video_info["like_count"]) / int(video_info["view_count"])

    if likes_to_views < 0.01:
        return 100
    elif likes_to_views < 0.015:
        return 60
    elif likes_to_views < 0.025:
        return 40
    elif likes_to_views < 0.03:
        return 30

    return 0


def get_comments_score(comments, comments_info):
    if len(comments) == 0:
        return 0

    clickbait_mentions_on_comment = comments_info["clickbait_mentions"] / len(comments)

    if clickbait_mentions_on_comment > 0.2:
        return 100
    elif clickbait_mentions_on_comment > 0.15:
        return 80
    elif clickbait_mentions_on_comment > 0.1:
        return 50
    elif clickbait_mentions_on_comment > 0.05:
        return 30
    elif clickbait_mentions_on_comment > 0.03:
        return 15

    return 0


# =============================================================

if __name__ == "__main__":
    app.run(debug=True)
