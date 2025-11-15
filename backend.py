from flask import Flask, request, jsonify
import cv2
import os
import tempfile

app = Flask(__name__)

def process_video_frames(video_path, frame_skip=30):
    """
    Reads a video file and yields one frame every 'frame_skip' frames.
    Also extracts a timestamp.
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_skip == 0:
            # Get timestamp in milliseconds
            timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            
            # Here, we would also get GPS data if available from a metadata file
            # gps_coord = get_gps_for_timestamp(timestamp_ms)
            
            yield frame, timestamp_ms
            
        frame_count += 1
        
    cap.release()
    print(f"Finished processing {video_path}")

@app.route('/process_video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No video file selected'}), 400
    
    # Save the uploaded video to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        video_file.save(temp_file.name)
        temp_path = temp_file.name
    
    try:
        # Process the video and count frames
        frame_count = 0
        timestamps = []
        for frame, timestamp in process_video_frames(temp_path):
            frame_count += 1
            timestamps.append(timestamp)
        
        # Mock AI processing results (since actual AI model is not implemented here)
        results = {
            'total_frames_processed': frame_count,
            'timestamps': timestamps[:10],  # Return first 10 timestamps as example
            'mock_detections': {
                'potholes': frame_count // 10,  # Mock detection count
                'cracks': frame_count // 15,
                'surface_wear': frame_count // 20
            },
            'processing_complete': True
        }
        
        return jsonify(results)
    
    finally:
        # Clean up temporary file
        os.unlink(temp_path)

if __name__ == '__main__':
    app.run(debug=True)
