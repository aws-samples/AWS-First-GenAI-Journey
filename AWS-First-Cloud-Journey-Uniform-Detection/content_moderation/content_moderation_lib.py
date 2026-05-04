
import boto3
import json
import sys
import cv2
import numpy as np
import tempfile
import os
from io import BytesIO
sys.path.append("../Libs")
import Libs as glib 

def extract_frames(video_bytes, num_frames=10):
    """Extract frames from video bytes with error handling"""
    try:
        # Save video bytes to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(video_bytes)
            temp_file_path = temp_file.name

        # Open video file
        cap = cv2.VideoCapture(temp_file_path)
        if not cap.isOpened():
            raise Exception("Error: Could not open video file")

        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 25  # Default to 25 fps if unable to determine

        if total_frames <= 0:
            # Try to count frames manually
            total_frames = 0
            while True:
                ret, _ = cap.read()
                if not ret:
                    break
                total_frames += 1
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset to beginning

        if total_frames <= 0:
            raise Exception("Error: Could not determine video length")

        duration = total_frames / fps
        frames = []
        timestamps = []

        # Calculate frame interval
        if total_frames < num_frames:
            num_frames = total_frames

        interval = max(1, total_frames // num_frames)

        # Extract frames
        frame_count = 0
        while len(frames) < num_frames:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % interval == 0:
                # Convert frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame_rgb)
                frames.append(buffer.tobytes())
                timestamps.append((frame_count / fps) if fps > 0 else frame_count / 25)

            frame_count += 1

        cap.release()

        # Cleanup
        try:
            os.unlink(temp_file_path)
        except:
            pass

        if not frames:
            raise Exception("Error: No frames could be extracted")

        return frames, timestamps, duration

    except Exception as e:
        raise Exception(f"Frame extraction error: {str(e)}")

def get_content_moderation_prompt(image_bytes=None):
    input_image_base64 = glib.get_base64_from_bytes(image_bytes)
    
    prompt = """Analyze this image for prohibited and sensitive content. If you are a geography expert, you may be able to identify political anomalies on the map. Pay special attention to:



1. **Political Sensitivity:**
   - **Prohibited Imagery:** Images related to China or containing maps with sensitive geopolitical content, specifically those depicting the nine-dash line (referred to as "đường lưỡi bò") or the U-shaped line, are strictly prohibited. This includes any maps displayed on walls or in relation to China that illustrate the nine-dash line.
   - **Restricted Flags:** The display of the yellow flag with three red stripes (commonly known as "cờ ba sọc") is not permitted.
   - **Disputed Territories:** Avoid maps that show contested regions or territories.
   - **Political Symbols:** The use of political symbols, gestures, or any imagery that suggests political stances is restricted.
   - **Flag Modifications:** Any alterations to national flags, symbols, or emblems that may imply political connotations are not allowed.
   - **Political Gatherings:** Images depicting political protests, gatherings, or demonstrations are strictly prohibited.
   - **Comprehensive Restrictions:** All images related to China and maps that clearly indicate the nine-dash line must be excluded.

2. **Adult/Inappropriate Content:**
   - **Explicit Material:** Content that is explicit or graphic in nature and deemed inappropriate for all age groups is restricted.
   - **Age-Restricted Content:** Any material that is age-restricted or inappropriate for a general audience is not allowed.
   - **Suggestive Imagery:** Imagery, text, or actions that are suggestive or imply adult themes are prohibited.
   - **Inappropriate Text Overlays:** Any text overlays, captions, or accompanying text that may be considered offensive or imply inappropriate content are not permitted.

3. **Other Prohibited Content:**
   - **Violent Imagery:** Content depicting violence or physical harm, including aggressive behavior, is restricted.
   - **Hate Symbols:** Symbols associated with hate groups or hate speech are strictly prohibited.
   - **Harassment and Bullying:** Content involving harassment, bullying, or any behavior intended to harm others is not allowed.
   - **Dangerous Activities:** Content promoting dangerous or reckless activities that could lead to unsafe behavior is restricted.
   - **Misinformation:** Content containing misinformation that may cause harm or promote false beliefs is not permitted.
   - **Offensive Gestures:** Any gestures or actions intended to offend or disrespect are strictly prohibited.


Provide a detailed analysis in this exact JSON format:
{
    "status": "SAFE/FLAG/BLOCK",
    "confidence": "HIGH/MEDIUM/LOW",
    "issues": {
        "political": {
            "detected": true/false,
            "type": ["list of detected political issues"],
            "confidence": "percentage"
        },
        "adult_content": {
            "detected": true/false,
            "type": ["list of detected inappropriate content"],
            "confidence": "percentage"
        },
        "other": {
            "detected": true/false,
            "type": ["list of other issues"],
            "confidence": "percentage"
        }
    },
    "action": "APPROVE/REVIEW/REMOVE",
    "explanation": "Brief explanation of the decision"
}

Return ONLY the JSON response with no additional text."""

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": input_image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    }
    return json.dumps(body)

def analyze_frame(session, frame):
    """Analyze a single frame with error handling"""
    try:
        body = get_content_moderation_prompt(frame)
        response = session.invoke_model_with_response_stream(
            body=body,
            modelId="anthropic.claude-sonnet-4-6",
            contentType="application/json",
            accept="application/json"
        )
        
        result = ""
        stream = response['body']
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    delta = json.loads(chunk.get('bytes').decode()).get("delta")
                    if delta:
                        result += delta.get("text", "")
        
        return json.loads(result)
    except Exception as e:
        print(f"Frame analysis error: {str(e)}")
        return None

def analyze_video_frames(frames, timestamps):
    """Analyze multiple frames with progress tracking and error handling"""
    try:
        session = boto3.Session()
        bedrock = session.client(service_name='bedrock-runtime')
        
        all_results = []
        for frame, timestamp in zip(frames, timestamps):
            try:
                frame_result = analyze_frame(bedrock, frame)
                if frame_result:
                    frame_result["timestamp"] = timestamp
                    all_results.append(frame_result)
            except Exception as e:
                print(f"Error analyzing frame at {timestamp}s: {str(e)}")
                continue

        if not all_results:
            raise Exception("No frames could be analyzed successfully")

        return aggregate_video_results(all_results)
    except Exception as e:
        raise Exception(f"Video analysis error: {str(e)}")

def get_response_from_model(prompt_content, content_bytes, content_type="image"):
    try:
        if content_type.lower() == "image":
            session = boto3.Session()
            bedrock = session.client(service_name='bedrock-runtime')
            body = get_content_moderation_prompt(content_bytes)
            
            response = bedrock.invoke_model_with_response_stream(
                body=body,
                modelId="anthropic.claude-sonnet-4-6",
                contentType="application/json",
                accept="application/json"
            )
            
            stream = response['body']
            if stream:
                for event in stream:
                    chunk = event.get('chunk')
                    if chunk:
                        try:
                            delta = json.loads(chunk.get('bytes').decode()).get("delta")
                            if delta:
                                yield delta.get("text")
                        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                            continue
        else:
            # Extract and analyze video frames
            frames, timestamps, duration = extract_frames(content_bytes)
            result = analyze_video_frames(frames, timestamps)
            if result:
                yield json.dumps(result)
            else:
                raise Exception("Video analysis produced no results")
    except Exception as e:
        raise Exception(f"Analysis error: {str(e)}")


# ... (previous code remains the same until analyze_video_frames function)


def aggregate_video_results(frame_results):
    """
    Aggregate results from multiple frames into a single comprehensive report
    with better timestamp handling
    """
    if not frame_results:
        raise Exception("No frame results to aggregate")

    # Initialize duration from last frame timestamp, with fallback
    try:
        duration = frame_results[-1].get('timestamp', 0)
    except:
        duration = 0

    aggregated = {
        "status": "SAFE",
        "confidence": "HIGH",
        "issues": {
            "political": {
                "detected": False,
                "type": [],
                "timestamps": [],
                "confidence": "0%"
            },
            "adult_content": {
                "detected": False,
                "type": [],
                "timestamps": [],
                "confidence": "0%"
            },
            "other": {
                "detected": False,
                "type": [],
                "timestamps": [],
                "confidence": "0%"
            }
        },
        "action": "APPROVE",
        "summary": {
            "total_frames": len(frame_results),
            "frames_with_issues": 0,
            "duration": f"{duration:.2f}s",
            "timeline": []
        },
        "explanation": "Video analysis summary:\n"
    }

    # Track issues and their frequencies
    issue_counts = {
        "political": {},
        "adult_content": {},
        "other": {}
    }

    # Process each frame
    frames_with_issues = 0
    for idx, result in enumerate(frame_results):
        # Get timestamp with fallback to frame index
        current_time = result.get('timestamp', idx / 25.0)  # Fallback to estimated time
        has_issues = False

        # Update status
        if result.get("status") == "BLOCK":
            aggregated["status"] = "BLOCK"
            aggregated["confidence"] = "HIGH"
            has_issues = True
        elif result.get("status") == "FLAG" and aggregated["status"] != "BLOCK":
            aggregated["status"] = "FLAG"
            has_issues = True

        # Process each issue type
        for issue_type in ["political", "adult_content", "other"]:
            issues = result.get("issues", {}).get(issue_type, {})
            if issues.get("detected"):
                aggregated["issues"][issue_type]["detected"] = True
                has_issues = True
                
                # Track issues
                for issue in issues.get("type", []):
                    if issue not in issue_counts[issue_type]:
                        issue_counts[issue_type][issue] = 1
                        aggregated["issues"][issue_type]["type"].append(issue)
                        aggregated["issues"][issue_type]["timestamps"].append(current_time)
                    else:
                        issue_counts[issue_type][issue] += 1

                # Update confidence
                current_confidence = issues.get("confidence", "0%")
                if current_confidence.endswith("%"):
                    current_value = int(current_confidence[:-1])
                    existing_value = int(aggregated["issues"][issue_type]["confidence"][:-1])
                    if current_value > existing_value:
                        aggregated["issues"][issue_type]["confidence"] = current_confidence

        if has_issues:
            frames_with_issues += 1
            aggregated["summary"]["timeline"].append({
                "time": current_time,
                "issues": [
                    issue_type for issue_type in ["political", "adult_content", "other"]
                    if result.get("issues", {}).get(issue_type, {}).get("detected", False)
                ]
            })

    # Update summary
    aggregated["summary"]["frames_with_issues"] = frames_with_issues

    # Set action
    if aggregated["status"] == "BLOCK":
        aggregated["action"] = "REMOVE"
        aggregated["explanation"] += "\nCritical issues detected requiring immediate removal:"
    elif aggregated["status"] == "FLAG":
        aggregated["action"] = "REVIEW"
        aggregated["explanation"] += "\nPotential issues detected requiring review:"
    else:
        aggregated["explanation"] += "\nNo significant issues detected."

    # Add issue details to explanation
    for issue_type in ["political", "adult_content", "other"]:
        if aggregated["issues"][issue_type]["detected"]:
            aggregated["explanation"] += f"\n\n{issue_type.replace('_', ' ').title()} Issues:"
            for issue, count in issue_counts[issue_type].items():
                percentage = (count / len(frame_results)) * 100
                aggregated["explanation"] += f"\n- {issue} (in {percentage:.1f}% of frames)"
            
            # Add first occurrences
            if aggregated["issues"][issue_type]["timestamps"]:
                aggregated["explanation"] += "\nFirst detections at:"
                for issue, time in zip(
                    aggregated["issues"][issue_type]["type"],
                    aggregated["issues"][issue_type]["timestamps"]
                ):
                    aggregated["explanation"] += f"\n- {issue}: {time:.2f}s"

    # Add statistics
    aggregated["explanation"] += f"\n\nAnalysis Summary:"
    aggregated["explanation"] += f"\n- Total frames: {aggregated['summary']['total_frames']}"
    aggregated["explanation"] += f"\n- Frames with issues: {frames_with_issues}"
    aggregated["explanation"] += f"\n- Duration: {aggregated['summary']['duration']}"
    
    clean_percentage = ((len(frame_results) - frames_with_issues) / len(frame_results)) * 100
    aggregated["explanation"] += f"\n- Clean frames: {clean_percentage:.1f}%"

    return aggregated

