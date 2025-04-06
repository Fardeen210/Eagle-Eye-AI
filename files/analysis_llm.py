import base64
import os
import csv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import time


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def encode_image(image_path):
    """Get the base64 string of an image."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def image_summarize(img_base64, prompt):
    """Generate an image summary using ChatOpenAI with image input."""
    chat = ChatOpenAI(model="gpt-4o-mini", max_tokens=1024)
    msg = chat.invoke([
        HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                }
            ]
        )
    ])
    return msg.content

def text_summarize(text):
    print("[AI] Generating text summary (overall scene)...")
    """Generate a text summary using ChatOpenAI with text input."""
    chat = ChatOpenAI(model="gpt-4o-mini", max_tokens=1024)
    msg = chat.invoke([HumanMessage(content=text)])
    return msg.content

def check_crime(summary):
    """Check if the provided summary contains crime-related keywords."""
    crime_keywords = [
        "crime", "criminal", "weapon", "gun", "robbery", 
        "assault", "shooting", "murder", "violence", "suspect"
    ]
    summary_lower = summary.lower()
    return any(keyword in summary_lower for keyword in crime_keywords)

def generate_img_summaries(folder_path):
    time.sleep(120)
    print(f"[PROCESS] Analyzing images in: {folder_path}")
    """
    Process images in a folder: encode, generate summaries, and check for crime-related content.
    
    Parameters:
        folder_path (str): Path to the folder containing image files.
        
    Returns:
        tuple: (list of base64 encoded images, list of image summaries, list of alert messages)
    """
    img_base64_list = []
    image_summaries = []
    alerts = []

    # Prompt for summarizing individual images from crime video frames.
    prompt = (
        "You are an assistant analyzing images from crime videos. "
        "For each image, give a short summary in no more than **50 words**. "
        "Include visible people, actions, clothing, and suspicious behavior. "
        "Be concise, clear, and only report what is visible."
    )
    
    # Process each image in the folder.
    for img_file in sorted(os.listdir(folder_path)):
        if img_file.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(folder_path, img_file)
            base64_image = encode_image(img_path)
            img_base64_list.append(base64_image)
            summary = image_summarize(base64_image, prompt)
            image_summaries.append(summary)
            # Check if this summary indicates a crime scene.
            if check_crime(summary):
                alerts.append(f"Alert for {img_file}: {summary}")

        print("[WAIT] Sleeping 2s between image summaries...\n")
        time.sleep(2)

    # Generate an overall summary from all image summaries.
    overall_prompt = (
    "Based on the following image summaries, write a short overall summary "
    "of the scene in **no more than 100 words**. Focus on the context, people, and "
    "any visible suspicious or criminal activity:\n" +
    "\n".join(image_summaries))

    time.sleep(5)

    overall_summary = text_summarize(overall_prompt)
    print(f"[OVERALL SUMMARY]\n{overall_summary}")
    if check_crime(overall_summary):
        alerts.append(f"Alert in overall summary: {overall_summary}")

    return img_base64_list, image_summaries, alerts, overall_summary

def get_top_video_folders(base_path, top_n=5):
    """Returns top N subfolders only (ignore direct images or non-folders)."""
    return sorted([
        f for f in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, f))
    ])[:top_n]


def save_to_csv(video_title, image_summaries, overall_summary, alerts, csv_file="summary_alerts.csv"):
    print(f"[SAVE COMPLETE] Entry saved for: {video_title}")
    """Save the summary and alerts to a CSV file."""
    joined_summaries = "\n---\n".join(image_summaries)
    joined_alerts = " | ".join(alerts)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([video_title, joined_summaries, overall_summary,joined_alerts])

# === MAIN ===
base_folder = "database/extrac_frames"
top_folders = get_top_video_folders(base_folder, top_n=10)

for folder_name in top_folders:
    folder_path = os.path.join(base_folder, folder_name)
    print(f"\n[PROCESSING] Folder: {folder_name}")
    img_base64_list, image_summaries, alerts,overall_summary = generate_img_summaries(folder_path)
    save_to_csv(folder_name,image_summaries, overall_summary,alerts)

    print("[WAIT] Sleeping for 10 seconds before processing the next folder...")
    time.sleep(10)

    if alerts:
        for alert in alerts:
            print(alert)
    else:
        print("No crime-related scenes detected.")
    