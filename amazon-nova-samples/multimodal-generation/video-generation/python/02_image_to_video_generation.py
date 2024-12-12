#!/usr/bin/env python3

import boto3
import logging
import json
import random
import base64
import amazon_video_util

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODEL_ID = "amazon.nova-reel-v1:0"

def setup_aws_session(region="us-east-1"):
    """Set up AWS session with default region"""
    boto3.setup_default_session(region_name=region)
    logger.info("AWS SDK session defaults have been set.")

def generate_video(s3_destination_bucket, input_image_path, video_prompt, model_id=DEFAULT_MODEL_ID):
    """
    Generate a video from an input image and prompt.
    
    Args:
        s3_destination_bucket (str): The S3 bucket where the video will be stored
        input_image_path (str): Path to the input image (must be 1280 x 720)
        video_prompt (str): Text prompt describing the desired video
    """
    # Set up the S3 client
    s3_client = boto3.client("s3")

    # Create the S3 bucket
    s3_client.create_bucket(Bucket=s3_destination_bucket)

    # Create the Bedrock Runtime client
    bedrock_runtime = boto3.client("bedrock-runtime")

    # Load the input image as a Base64 string
    with open(input_image_path, "rb") as f:
        input_image_bytes = f.read()
        input_image_base64 = base64.b64encode(input_image_bytes).decode("utf-8")

    model_input = {
        "taskType": "TEXT_VIDEO",
        "textToVideoParams": {
            "text": video_prompt,
            "images": [
                {
                    "format": "png",  # May be "png" or "jpeg"
                    "source": {
                        "bytes": input_image_base64
                    }
                }
            ]
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
    VIDEO_PROMPT = "Closeup of a large seashell in the sand, gentle waves flow around the shell. Camera zoom in."
    INPUT_IMAGE_PATH = "../images/sample-frame-1.png"  # Must be 1280 x 720
    MODEL_ID = "amazon.nova-reel-v1:0"

    # Generate the video
    invocation_arn = generate_video(S3_BUCKET, INPUT_IMAGE_PATH, VIDEO_PROMPT, MODEL_ID)
    if not invocation_arn:
        logger.error("Failed to start video generation")
        exit(1)
    
    # Monitor and download the video
    logger.info("\nMonitoring job and waiting for completion...")
    local_file_path = amazon_video_util.monitor_and_download_video(invocation_arn, "output")

    if local_file_path:
        logger.info(f"\nVideo successfully generated and downloaded to: {local_file_path}")
    else:
        logger.info("\nFailed to generate or download video")

if __name__ == "__main__":
    main()