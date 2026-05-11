"""
shared/image_lib.py — Amazon Nova Canvas image generation utility shared across projects.

Used by:
  - AWS-First-Cloud-Journey-Uniform-Detection
  - Content-Moderation-with-Amazon-Bedrock
  - Location-Analysis-System-with-Amazon-Bedrock
  - Product-Description-Generator-with-Amazon-Bedrock
  - TapVision-with-Amazon-Bedrock

To use in a project's image_lib.py:
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from shared.image_lib import get_image_response, get_response_image_from_payload
"""

import os
import boto3
import json
import base64
from io import BytesIO

session = boto3.Session(
    profile_name=os.environ.get("BWB_PROFILE_NAME")
)

bedrock = session.client(
    service_name="bedrock-runtime",
    region_name=os.environ.get("BWB_REGION_NAME"),
    endpoint_url=os.environ.get("BWB_ENDPOINT_URL"),
)

bedrock_model_id = "amazon.nova-canvas-v1:0"


def get_response_image_from_payload(response):
    """Extract and decode the image bytes from a Bedrock model response."""
    payload = json.loads(response.get("body").read())
    images = payload.get("artifacts")
    image_data = base64.b64decode(images[0].get("base64"))
    return BytesIO(image_data)


def get_image_response(prompt_content):
    """Generate an image from a text prompt using Amazon Nova Canvas."""
    request_body = json.dumps(
        {
            "text_prompts": [{"text": prompt_content}],
            "cfg_scale": 9,
            "steps": 50,
        }
    )

    response = bedrock.invoke_model(body=request_body, modelId=bedrock_model_id)
    return get_response_image_from_payload(response)
