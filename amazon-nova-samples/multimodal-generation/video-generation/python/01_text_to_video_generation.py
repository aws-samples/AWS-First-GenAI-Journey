#!/usr/bin/env python3

import boto3
import logging
import json
import random
import amazon_video_util
from datetime import datetime, timedelta, timezone

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODEL_ID = "amazon.nova-reel-v1:0"

def setup_aws_session(region="us-east-1"):
    """Set up AWS session with default region"""
    boto3.setup_default_session(region_name=region)
    logger.info("AWS SDK session defaults have been set.")


def generate_video(s3_destination_bucket, video_prompt, model_id=DEFAULT_MODEL_ID):
    """
    Generate a video using the provided prompt.
    
    Args:
        s3_destination_bucket (str): The S3 bucket where the video will be stored
        video_prompt (str): Text prompt describing the desired video
    """
    # Set up the S3 client
    s3_client = boto3.client("s3")

    # Create the S3 bucket
    s3_client.create_bucket(Bucket=s3_destination_bucket)

    # Create the Bedrock Runtime client
    bedrock_runtime = boto3.client("bedrock-runtime")

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

def check_job_status(invocation_arn):
    """Check status of a specific job using get_async_invoke()"""
    bedrock_runtime = boto3.client("bedrock-runtime")
    try:
        response = bedrock_runtime.get_async_invoke(
            invocationArn=invocation_arn
        )
        
        status = response["status"]
        logger.info(f"Status: {status}")
        logger.info("\nFull response:")
        logger.info(json.dumps(response, indent=2, default=str))
        return response
    except Exception as e:
        logger.error(f"Error checking job status: {e}")
        return None

def list_job_statuses(max_results=10, status_filter="InProgress"):
    """List all video generation jobs with optional filtering"""
    bedrock_runtime = boto3.client("bedrock-runtime")
    try:
        invocation = bedrock_runtime.list_async_invokes(
            maxResults=max_results,
            statusEquals=status_filter,
        )
        
        logger.info("Invocation Jobs:")
        logger.info(json.dumps(invocation, indent=2, default=str))
        return invocation
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        return None

def monitor_recent_jobs(duration_hours=1):
    """Monitor and download videos from the past N hours"""
    from_submit_time = datetime.now(timezone.utc) - timedelta(hours=duration_hours)
    return amazon_video_util.monitor_and_download_videos("output", submit_time_after=from_submit_time)


def main():
    # Initialize the AWS session
    setup_aws_session()

    # Configuration
    S3_BUCKET = "nova-videos"  # Change this to your unique bucket name
    VIDEO_PROMPT = "Closeup of a large seashell in the sand, gentle waves flow around the shell. Camera zoom in."
    MODEL_ID = "amazon.nova-reel-v1:0"

    # Generate video
    invocation_arn = generate_video(S3_BUCKET, VIDEO_PROMPT, MODEL_ID)
    if not invocation_arn:
        logger.error("Failed to start video generation")
        exit(1)

    # Check initial status
    logger.info("\nChecking initial job status...")
    check_job_status(invocation_arn)

    # List all in-progress jobs
    logger.info("\nListing all in-progress jobs...")
    list_job_statuses()

    # Monitor and download the video
    logger.info("\nMonitoring job and waiting for completion...")
    local_file_path = amazon_video_util.monitor_and_download_video(invocation_arn, "output")

    if local_file_path:
        logger.info(f"\nVideo successfully generated and downloaded to: {local_file_path}")
    else:
        logger.info("\nFailed to generate or download video")

if __name__ == "__main__":
    main()