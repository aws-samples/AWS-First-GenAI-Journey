import boto3
import json
import sys

sys.path.append("../Libs")

import Libs as glib 


#get the stringified request body for the InvokeModel API call
def get_product_description(prompt, image_bytes=None, prizm=None):
    input_image_base64 = glib.get_base64_from_bytes(image_bytes)
    prompt ="""\n\nHuman Here's a prompt for a product description that follows PRIZM marketing principles in Vietnamese:

Create a compelling product description for a new smart home device, targeting a specific PRIZM segment. Your description should:

1. Identify a particular PRIZM segment (e.g., "Young Digerati," "Bohemian Mix," or "Middleburg Managers") and tailor the messaging to their lifestyle and values.

2. Highlight the product's key features and benefits in a way that resonates with the chosen segment's interests and needs.

3. Use language, tone, and cultural references that appeal to the selected demographic.

4. Incorporate relevant lifestyle elements that the chosen segment would find attractive (e.g., tech-savviness, environmental consciousness, or family-oriented features).

5. Address potential pain points or desires specific to the selected PRIZM segment.

6. Include a brief explanation of how the product fits into and enhances the daily life of the target consumer.

7. Mention any exclusive or premium aspects that would appeal to the segment's socioeconomic status.

8. If applicable, reference complementary products or services that align with the segment's typical purchasing habits.

9. Use imagery or descriptive language that evokes the environments where the target segment typically lives or aspires to live.

10. Conclude with a call-to-action that speaks directly to the motivations of the chosen PRIZM segment.

The description should be approximately 500-750 words long and seamlessly integrate PRIZM segmentation insights while maintaining a natural, persuasive tone.
\n\n Assistant:"""
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
                        "text": prizm
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


def get_response_from_model(prompt_content, image_bytes, prizm):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime') #creates a Bedrock client
    body = get_product_description(prompt_content, image_bytes, prizm)    
    response = bedrock.invoke_model_with_response_stream(body=body, modelId="anthropic.claude-3-5-sonnet-20240620-v1:0", contentType="application/json", accept="application/json")
        
    stream = response['body']
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                 delta = json.loads(chunk.get('bytes').decode()).get("delta")
                 if delta:
                     yield delta.get("text")    
