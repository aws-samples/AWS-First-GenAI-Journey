import boto3
import json
import logging
import sys
sys.path.append("../Libs")
import Libs as glib 

logger = logging.getLogger(__name__)

def get_product_description(prompt, image_bytes=None, prizm=None):
    input_image_base64 = glib.get_base64_from_bytes(image_bytes)
    
    marketing_guidelines = """
    Create a comprehensive product description following these marketing principles:

    1. Target Audience Analysis:
    - Identify key demographic segments
    - Understand lifestyle patterns and preferences
    - Map consumer behavior and buying habits
    
    2. Product Feature Presentation:
    - Core functionality and specifications
    - Unique selling propositions
    - Technical specifications and compatibility
    - Design elements and aesthetics
    
    3. Benefits and Value Proposition:
    - Primary benefits for target segment
    - Problem-solving capabilities
    - Lifestyle enhancement aspects
    - Integration with existing ecosystem
    
    4. Brand Positioning:
    - Premium/luxury vs value positioning
    - Market differentiation points
    - Brand voice and personality
    - Quality assurance elements
    
    5. Experience Description:
    - User experience highlights
    - Ease of use and accessibility
    - Setup and maintenance
    - Customer support features
    
    6. Social Proof Elements:
    - Usage scenarios and case studies
    - Testimonial integration points
    - Expert endorsements if applicable
    - Awards and certifications
    
    7. Technical Specifications:
    - Detailed specifications list
    - Compatibility requirements
    - Maintenance guidelines
    - Warranty information
    
    Output Format:
    {
        "product_name": "Product name",
        "target_segment": {
            "primary_audience": "",
            "secondary_audience": "",
            "lifestyle_profile": ""
        },
        "key_features": [
            {"feature": "", "benefit": ""}
        ],
        "technical_specs": {
            "dimensions": "",
            "compatibility": "",
            "requirements": ""
        },
        "marketing_description": {
            "short_description": "50 words",
            "detailed_description": "300 words",
            "key_benefits": [],
            "use_cases": []
        },
        "pricing_positioning": {
            "price_point": "",
            "market_segment": "",
            "competitive_advantage": ""
        }
    }
    """

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
                        "text": f"PRIZM Segmentation Data:\n{prizm}\n\nMarketing Guidelines:\n{marketing_guidelines}\n\nAnalyze the provided image and create a detailed product description following the above format. Focus on features visible in the image and align with the PRIZM segmentation data. Return only JSON format."
                    }
                ],
            }
        ],
    }
    return json.dumps(body)

def get_response_from_model(prompt_content, image_bytes, prizm):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime')
    body = get_product_description(prompt_content, image_bytes, prizm)    
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
                except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as e:
                    logger.warning(f"Failed to parse stream chunk: {e}")
                    continue