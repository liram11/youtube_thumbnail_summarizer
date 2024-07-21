from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/api/v1/video-summary', methods=['GET'])
def get_video_summary():
    video_id = request.args.get('video_id')

    full_transcript = download_full_transcript('3N4m5k9GAW0')

    return jsonify({
        "tr": full_transcript
    })


def download_full_transcript(video_id):
    transcripts = YouTubeTranscriptApi.get_transcript(video_id)

    full_transcript = ''
    for transcript in transcripts:
        full_transcript += transcript['text'] + ' '

    return full_transcript



if __name__ == '__main__':
    app.run(debug=True)
