import boto3
import json
import sys
sys.path.append("../Libs")
import Libs as glib 

def get_content_moderation_prompt(image_bytes=None):
    input_image_base64 = glib.get_base64_from_bytes(image_bytes)
    
    prompt = """Analyze this image for prohibited and sensitive content. Pay special attention to:

1. Political Sensitivity:
   - Yellow flag with three red stripes ("cờ ba sọc")
   - Nine-dash line or U-shaped line ("đường lưỡi bò")
   - Maps showing disputed territories
   - Political symbols

2. Adult/Inappropriate Content:
   - Explicit material
   - Age-restricted content
   - Inappropriate imagery

3. Other Prohibited Content:
   - Violence
   - Hate symbols
   - Harassment

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

def get_response_from_model(prompt_content, image_bytes):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')
    body = get_content_moderation_prompt(image_bytes)    
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