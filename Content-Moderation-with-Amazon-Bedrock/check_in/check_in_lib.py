import boto3
import json
import base64
from io import BytesIO
import sys
sys.path.append("../Libs")
import Libs as glib 

def get_image_understanding_request_body(prompt, image_bytes, mask_prompt=None):
    input_image_base64 = glib.get_base64_from_bytes(image_bytes)
    
    # Detailed classification criteria in English
    location_criteria = """
        Analyze the location based on these detailed criteria:

        1. OFFICE ENVIRONMENT:
        Physical Features:
        - Workstations with computers/laptops
        - Meeting/conference rooms
        - Office furniture (ergonomic chairs, desks)
        - Whiteboards/presentation screens
        
        Professional Elements:
        - Corporate branding/logos
        - Professional décor
        - Business-related posters/notices
        - Employee workspace organization
        
        Technology:
        - Computer monitors
        - Office equipment (printers, phones)
        - Network/IT infrastructure
        - Professional lighting

        2. RESTAURANT/BAR:
        Dining Area:
        - Dining tables and chairs
        - Bar counter/seating
        - Table settings (glasses, cutlery)
        - Menu displays
        
        Service Features:
        - Beer taps/drink stations
        - Refrigerators/coolers
        - Service counters
        - Food/drink storage
        
        Ambiance:
        - Restaurant signage
        - Beer brand displays
        - Ambient lighting
        - Entertainment features

        3. RETAIL STORE:
        Store Layout:
        - Product shelving/displays
        - Point of sale/checkout area
        - Shopping aisles
        - Storage/stock area
        
        Retail Elements:
        - Price tags/labels
        - Product advertisements
        - Shopping baskets/carts
        - Store signage
        
        Equipment:
        - Cash registers
        - Display refrigerators
        - Security systems
        - Inventory storage

        4. OTHER LOCATIONS:
        Public Spaces:
        - Parks/recreational areas
        - Educational facilities
        - Community centers
        - Public transport areas
        
        Residential:
        - Living spaces
        - Residential buildings
        - Private areas
        - Home environments
        
        Outdoor:
        - Streets/sidewalks
        - Parking areas
        - Green spaces
        - Public infrastructure
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
                        }
                    },
                    {
                        "type": "text",
                        "text": f"{location_criteria}\n\nBased on the image and above criteria, analyze and return a JSON response with the following structure:\n" + 
                               "{\n" +
                               "  'location_type': 'office/restaurant/retail/other',\n" +
                               "  'confidence': 'high/medium/low',\n" +
                               "  'key_features': ['feature1', 'feature2', ...],\n" +
                               "  'environment': {\n" +
                               "    'lighting': 'bright/moderate/dim',\n" +
                               "    'space_size': 'large/medium/small',\n" +
                               "    'occupancy': 'high/moderate/low',\n" +
                               "    'cleanliness': 'excellent/good/fair'\n" +
                               "  },\n" +
                               "  'specific_identifiers': ['identifier1', 'identifier2', ...],\n" +
                               "  'business_indicators': ['indicator1', 'indicator2', ...],\n" +
                               "  'primary_purpose': 'brief description of main use',\n" +
                               "  'secondary_characteristics': ['characteristic1', 'characteristic2', ...],\n" +
                               "  'safety_compliance': {\n" +
                               "    'emergency_exits': 'visible/not visible',\n" +
                               "    'safety_equipment': 'present/not visible',\n" +
                               "    'accessibility': 'good/limited/unknown'\n" +
                               "  },\n" +
                               "  'analysis_quality': {\n" +
                               "    'image_clarity': 'high/medium/low',\n" +
                               "    'visibility_of_features': 'good/partial/limited',\n" +
                               "    'analysis_confidence': 'high/medium/low'\n" +
                               "  },\n" +
                               "  'explain': 'detailed explanation of classification'\n" +
                               "}\n" +
                               "Return only JSON format, no additional text."
                    }
                ]
            }
        ]
    }
    
    return json.dumps(body)

def get_response_from_model(prompt_content=None, image_bytes=None, mask_prompt=None):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime') 
    body = get_image_understanding_request_body(prompt_content, image_bytes, mask_prompt=mask_prompt)
    
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