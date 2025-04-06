import pandas as pd
from sentence_transformers import SentenceTransformer, util
import math

df = pd.read_csv("summary_alerts.csv", encoding="ISO-8859-1", names=["video_title", "overall_summary", "scene_summary", "alerts"])  # aka latin1

# Load the model only once (outside the loop)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Suspect description
suspect_desc = "A woman in black tank top and wearing grey pants. She is wearing white shoes and has a ponytail."

# Encode the suspect description once
suspect_embedding = model.encode(suspect_desc, convert_to_tensor=True)

# Loop over each row in the DataFrame
for index, row in df.iterrows():
    summary = str(row["overall_summary"])  # Ensure it's a string
    # print(summary)
    summary_embedding = model.encode(summary, convert_to_tensor=True)

    # Compute cosine similarity
    similarity_score = util.cos_sim(suspect_embedding, summary_embedding).item()
    if round(similarity_score, 2) >= 0.15:
      print(f"The person description that has been provided has been matched in the video with title: {row['video_title']}")


