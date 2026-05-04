import boto3
import json
import base64
from io import BytesIO
import sys
sys.path.append("../Libs")
import Libs as glib 

def get_check_uniform_request_body(image_bytes=None):
    # Load AWS First Cloud Journey uniform examples
    aws_uniforms = []
    for i in range(1, 9):  # Load 8 example images
        path = f"./check_uniform/images/{i:04d}.jpg"  # Format: 0001.jpg, 0002.jpg, etc.
        try:
            uniform_bytes = glib.get_bytes_from_file(path)
            aws_uniforms.append(glib.get_base64_from_bytes(uniform_bytes))
        except Exception as e:
            print(f"Error loading image {i}: {str(e)}")
            continue

    input_image_base64 = glib.get_base64_from_bytes(image_bytes)
    
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "These are images of people wearing AWS First Cloud Journey shirts:"
                    }
                ]
            }
        ]
    }

    # Add example images to content
    for idx, uniform in enumerate(aws_uniforms, 1):
        body["messages"][0]["content"].extend([
            {
                "type": "text",
                "text": f"Image {idx}:"
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": uniform,
                }
            }
        ])

    # Add analysis instructions
    body["messages"][0]["content"].extend([
        {
            "type": "text",
            "text": "In this image:"
        },
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": input_image_base64,
            }
        },
        {
            "type": "text",
            "text": "As a supervisor, please determine: 1. If there are any faces in the image 2. If the person is wearing an AWS First Cloud Journey shirt. Follow these steps:"
        },
        {
            "type": "text",
            "text": "1. Identify if there are any faces in the image\n2. Compare their clothing with the AWS First Cloud Journey shirts shown above\n3. If you see text mentioning 'AWS First Cloud Journey' or AWS cloud certification badges on the shirt, conclude they are wearing an AWS First Cloud Journey shirt\n4. If only a face is visible with no clear view of clothing, conclude they are not wearing an AWS First Cloud Journey shirt\n5. If the image is too blurry or dark to compare with the examples above, conclude they are not wearing an AWS First Cloud Journey shirt"
        },
        {
            "type": "text",
            "text": "Return only a JSON response with the conclusion about faces and AWS First Cloud Journey shirt wearing status. No additional explanations."
        },
        {
            "type": "text",
            "text": "{isConfirm:'wearing AWS First Cloud Journey shirt / not wearing AWS First Cloud Journey shirt', explain:'brief explanation why'}"
        },
        {
            "type": "text",
            "text": "Return only JSON format"
        }
    ])
    
    return json.dumps(body)

def get_response_from_model(image_bytes):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime') 
    body = get_check_uniform_request_body(image_bytes)
    
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
                delta = json.loads(chunk.get('bytes').decode()).get("delta")
                if delta:
                    yield delta.get("text")