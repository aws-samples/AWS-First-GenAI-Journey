#!/usr/bin/env python3

import os
import boto3
import logging
import json
import random
import base64
import amazon_video_util
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODEL_ID = "amazon.nova-reel-v1:0"

def setup_aws_session(region="us-east-1"):
    """Set up AWS session with default region"""
    boto3.setup_default_session(region_name=region)
    logger.info("AWS SDK session defaults have been set.")

def generate_video(s3_destination_bucket, video_prompt, input_image_path=None, model_id=DEFAULT_MODEL_ID):
    """
    Generate a video from an input image and prompt or from the prompt alone.
    
    Args:
        s3_destination_bucket (str): The S3 bucket where the video will be stored
        video_prompt (str): Text prompt describing the desired video
        input_image_path (str): Optional path to the input image (must be 1280 x 720)
        model_id (str): The model ID to use for video generation (default is DEFAULT_MODEL_ID)
    """
    # Set up the S3 client
    s3_client = boto3.client("s3")

    # Create the S3 bucket
    s3_client.create_bucket(Bucket=s3_destination_bucket)

    # Create the Bedrock Runtime client
    bedrock_runtime = boto3.client("bedrock-runtime")

    # Initialize model input
    model_input = {
        "taskType": "TEXT_VIDEO",
        "textToVideoParams": {
            "text": video_prompt,
        },
        "videoGenerationConfig": {
            "durationSeconds": 6,  # 6 is the only supported value currently
            "fps": 24,  # 24 is the only supported value currently
            "dimension": "1280x720",  # "1280x720" is the only supported value currently
            "seed": random.randint(
                0, 2147483648
            ),  # A random seed guarantees we'll get a different result each time this code runs
        },
    }

    # If an input image path is provided, add it to the model input
    if input_image_path:
        with open(input_image_path, "rb") as f:
            input_image_bytes = f.read()
            input_image_base64 = base64.b64encode(input_image_bytes).decode("utf-8")
        model_input["textToVideoParams"]["images"] = [
            {
                "format": "png",  # May be "png" or "jpeg"
                "source": {
                    "bytes": input_image_base64
                }
            }
        ]

    try:
        # Start the asynchronous video generation job
        invocation = bedrock_runtime.start_async_invoke(
            modelId=model_id,
            modelInput=model_input,
            outputDataConfig={"s3OutputDataConfig": {"s3Uri": f"s3://{s3_destination_bucket}"}},
        )

        # Store the invocation ARN
        invocation_arn = invocation["invocationArn"]

        # Pretty print the response JSON
        logger.info("\nResponse:")
        logger.info(json.dumps(invocation, indent=2, default=str))

        # Save the invocation details for later reference
        amazon_video_util.save_invocation_info(invocation, model_input)

        return invocation_arn

    except Exception as e:
        logger.error(e)
        return None
    


def main():
    # Initialize the AWS session
    setup_aws_session()

    # Configuration
    S3_BUCKET = "nova-videos"  # Change this to your unique bucket name
    VIDEO_PROMPT_1 = "First person view walking through light snowfall in a forest, sunlight through trees, dolly forward, cinematic"
    VIDEO_PROMPT_2 = "First person view entering a clearing with heavy snowfall, sun creating diamond-like sparkles, continuing dolly forward, cinematic"
    MODEL_ID = "amazon.nova-reel-v1:0"

    # Generate the first video
    invocation_arn_1 = generate_video(S3_BUCKET, VIDEO_PROMPT_1, None, MODEL_ID)
    if not invocation_arn_1:
        logger.error("Failed to start video generation")
        exit(1)
    
    # Monitor and download the video
    logger.info("\nMonitoring job and waiting for completion...")
    local_file_path_1 = amazon_video_util.monitor_and_download_video(invocation_arn_1, "output")

    if local_file_path_1:
        logger.info(f"\nVideo successfully generated and downloaded to: {local_file_path_1}")
    else:
        logger.info("\nFailed to generate or download video")

    # Define and create an output directory with a unique name.
    generation_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_directory = f"./output/{generation_id}"
    os.makedirs(output_directory, exist_ok=True)

    # Extract the last frame from the video
    last_frame_path = f"{output_directory}/last_frame.png"
    amazon_video_util.extract_last_frame(local_file_path_1, last_frame_path)

    # Generate the second video
    invocation_arn_2 = generate_video(S3_BUCKET, VIDEO_PROMPT_2, last_frame_path, MODEL_ID)
    if not invocation_arn_2:
        logger.error("Failed to start video generation")
        exit(1)

    # Monitor and download the video
    logger.info("\nMonitoring job and waiting for completion...")
    local_file_path_2 = amazon_video_util.monitor_and_download_video(invocation_arn_2, "output")

    if local_file_path_2:
        logger.info(f"\nVideo successfully generated and downloaded to: {local_file_path_2}")
    else:
        logger.info("\nFailed to generate or download video")

    # Create output path for merged video
    output_path = f"{output_directory}/merged_video.mp4"

    # Stitch the two video generations together
    amazon_video_util.stitch_videos(local_file_path_1, local_file_path_2, output_path)

if __name__ == "__main__":
    main()