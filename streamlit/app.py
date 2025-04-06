import streamlit as st
import os
import base64
import csv
from streamlit.components.v1 import html

# Set page layout
st.set_page_config(page_title="🎬 Video Analysis", layout="wide")
st.title("🎥 CCTV footage with AI Analysis")

# Folder where videos are stored
VIDEO_DIR = "database"
SUMMARY_CSV = "summary_alerts.csv"  # CSV must match earlier save format

# Fixed size for videos
fixed_width = 480
fixed_height = 270

# Load video files
video_files = [
    f for f in os.listdir(VIDEO_DIR)
    if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
]

# Load summaries/alerts from CSV
video_summaries = {}
if os.path.exists(SUMMARY_CSV):
    with open(SUMMARY_CSV, newline='', encoding='ISO-8859-1', errors='replace') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 3:
                title, overall_summary, alerts = row[0], row[1], row[2]
                video_summaries[title] = {
                    "summary": overall_summary,
                    "alerts": alerts
                }

if not video_files:
    st.warning("⚠️ No videos found in the 'Videos/' folder.")
else:
    # HTML structure for 3-in-a-row layout with summaries
    html_videos = """
<style>
    .video-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
    }
    .video-card {
        background: #f9f9f9;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: row;
        height: auto;
    }
    .video-box {
        width: 50%;
        max-width: 480px;
        height: 270px;
        overflow: hidden;
        border-radius: 8px;
        background: #000;
    }
    .video-box video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .summary-box {
        width: 50%;
        padding-left: 15px;
        font-family: sans-serif;
        font-size: 14px;
    }
    .summary-box strong {
        display: block;
        margin-bottom: 8px;
        font-size: 16px;
        color: #222;
    }
    .summary-box .alert {
        margin-top: 10px;
        color: red;
        font-weight: bold;
    }
</style>
<div class="video-grid">
    """

    for video_file in video_files:
        video_name = os.path.splitext(video_file)[0]
        video_path = os.path.join(VIDEO_DIR, video_file)

        with open(video_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        # Load summary and alerts if available
        #summary_text = video_summaries.get(video_name, {}).get("summary", "No summary available.")
        alert_text = video_summaries.get(video_name, {}).get("alerts", "")

        video_html = f"""
<div class="video-card">
    <div class="video-box">
        <video autoplay muted loop playsinline>
            <source src="data:video/mp4;base64,{encoded}" type="video/mp4">
        </video>
    </div>
    <div class="summary-box">
        <strong>Summary for: {video_name}</strong>
        {"<p class='alert'>🚨 Alerts: " + alert_text + "</p>" if alert_text else ""}
    </div>
</div>
        """
        html_videos += video_html

    html_videos += "</div>"

    # Render in Streamlit
    html(html_videos, height=1500, scrolling=True)
