import boto3
import json
import sys

sys.path.append("../Libs")

import Libs as glib 


def get_product_description(prompt, image_bytes=None):
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
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg", #this doesn't seem to matter?
                            "data": input_image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    },
                ],
            }
        ],
    }
    return json.dumps(body)


def get_response_from_model(prompt_content, image_bytes):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime') #creates a Bedrock client
    body = get_product_description(prompt_content, image_bytes)    
    response = bedrock.invoke_model_with_response_stream(body=body, modelId="anthropic.claude-3-5-sonnet-20240620-v1:0", contentType="application/json", accept="application/json")
        
    stream = response['body']
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                 delta = json.loads(chunk.get('bytes').decode()).get("delta")
                 if delta:
                     yield delta.get("text")    

prompt ="""\n\nYou are an AI content moderation assistant. Your task is to review and assess user-generated content for a social media platform. 
The content may include text posts, comments, images, and video descriptions. 
Your goal is to identify and flag potentially problematic content that violates the platform's community guidelines.

Please review the following content and provide:

A classification of the content as either "Safe," "Requires Review," or "Violates Guidelines"
A brief explanation of your decision
Specific categories of concern, if any (e.g., hate speech, violence, sexual content, harassment, misinformation)
Suggested actions (e.g., remove content, issue warning, age-restrict)
Consider the following guidelines when moderating:

Hate speech or discrimination based on race, ethnicity, gender, religion, etc. is not allowed
Explicit violence or gore is prohibited
Sexually explicit content should be age-restricted
Harassment or bullying of individuals is not permitted
Misinformation that could cause harm should be flagged
Nine-dash line or U line of south China
Context and intent should be considered when possible

Please provide your assessment for the following content:

Remember to be objective and consistent in your evaluations, and explain your reasoning clearly.
\n\n Assistant:"""