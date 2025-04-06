import os
import cv2

class FrameExtractor:
    def __init__(self, video_folder, output_root, default_interval_sec=1, custom_intervals=None):
        self.video_folder = video_folder
        self.output_root = output_root
        self.default_interval_sec = default_interval_sec
        self.custom_intervals = custom_intervals or {}

        os.makedirs(self.output_root, exist_ok=True)
        print(f"[INIT] FrameExtractor initialized. Saving frames to '{self.output_root}'")

    def get_interval_for_video(self, video_name):
        return self.custom_intervals.get(video_name, self.default_interval_sec)

    def extract_frames_from_all_videos(self):
        for file in os.listdir(self.video_folder):
            if file.lower().endswith((".mp4", ".avi", ".mov")):
                video_path = os.path.join(self.video_folder, file)
                self.extract_frames_from_video(video_path)

    def extract_frames_from_video(self, video_path):
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        interval_sec = self.get_interval_for_video(video_name)
        output_dir = os.path.join(self.output_root, video_name)
        os.makedirs(output_dir, exist_ok=True)

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        interval_frames = int(fps * interval_sec)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"[INFO] Processing '{video_name}' | Interval: {interval_sec}s | Total frames: {total_frames}")

        frame_idx = 0
        saved_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % interval_frames == 0:
                timestamp_sec = frame_idx / fps

                frame_filename = f"frame{frame_idx}_t{int(timestamp_sec)}s.jpg"

                frame_path = os.path.join(output_dir, frame_filename)

                cv2.imwrite(frame_path, frame)
                saved_count += 1
                print(f"  - Saved: {frame_filename}")

            frame_idx += 1

        cap.release()
        print(f"[DONE] Extracted {saved_count} frames from '{video_name}' into '{output_dir}'")

if __name__ == "__main__":
    custom_intervals = {
        "database/normal video": 3,   # Every 1 second
        "suspicious_car": 1,  # Every 0.5 seconds
    }

    extractor = FrameExtractor(
        video_folder="database",
        output_root="database/extrac_frames",
        default_interval_sec=1,
        custom_intervals=custom_intervals
    )

    extractor.extract_frames_from_all_videos()
