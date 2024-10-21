import os
import boto3, json
from dotenv import load_dotenv
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA
from langchain_community.chat_models import BedrockChat
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import base64
from io import BytesIO

load_dotenv()

def call_claude_sonet_stream(prompt):

    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "temperature": 1, 
        "top_k": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }

    body = json.dumps(prompt_config)

    modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    accept = "application/json"
    contentType = "application/json"

    bedrock = boto3.client(service_name="bedrock-runtime")  
    response = bedrock.invoke_model_with_response_stream(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )

    stream = response['body']
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                 delta = json.loads(chunk.get('bytes').decode()).get("delta")
                 if delta:
                     yield delta.get("text")    




#get a BytesIO object from file bytes
def get_bytesio_from_bytes(image_bytes):
    image_io = BytesIO(image_bytes)
    return image_io


#get a base64-encoded string from file bytes
def get_base64_from_bytes(image_bytes):
    resized_io = get_bytesio_from_bytes(image_bytes)
    img_str = base64.b64encode(resized_io.getvalue()).decode("utf-8")
    return img_str


#load the bytes from a file on disk
def get_bytes_from_file(file_path):
    with open(file_path, "rb") as image_file:
        file_bytes = image_file.read()
    return file_bytes

def init(prompt, image_bytes=None):  

    if image_bytes:
        input_image_base64 = get_base64_from_bytes(image_bytes)
        content = [
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
                    },
        ]
    else:
         content =  [{
                    "type": "text",
                    "text": prompt
                }]
   
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
    }
    return json.dumps(body)

def get_response_from_model(prompt_content, image_bytes):
    session = boto3.Session()
    bedrock = session.client(service_name='bedrock-runtime') #creates a Bedrock client
    body = init(prompt_content, image_bytes)    
    response = bedrock.invoke_model_with_response_stream(body=body, modelId="anthropic.claude-3-5-sonnet-20240620-v1:0", contentType="application/json", accept="application/json")
        
    stream = response['body']
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                 delta = json.loads(chunk.get('bytes').decode()).get("delta")
                 if delta:
                     yield delta.get("text")    

prizm = """
    {
      "hh_employment": "Mix",
      "code": "63",
      "pzp_gcode": "63",
      "lifestage_group_name": "Striving Singles",
      "segment_icon_name": "63_low_rise_living.png",
      "hh_composition": "Mostly w/o Kids",
      "lifestage_super_group_name": "D70036",
      "segment_lifestage_group": "03",
      "demographic_caption": "Lower Mid(Scale) Middle Age Mostly w/o Kids",
      "social_group_name": "Urban Cores",
      "segment_nickname": "Low-Rise Living",
      "pzp_code": "63",
      "lifestyle_trait1": "Owns a Mitsubishi",
      "hh_tenure": "Renters",
      "lifestyle_trait2": "Eats at Starbucks",
      "lifestyle_trait3": "Shops at Banana Republic",
      "urbanicity": "Urban",
      "hh_income": "Lower Mid(Scale)",
      "hh_education": "Some College",
      "lifestage_group_rank": 16,
      "segment_narrative": "The most economically challenged urban segment, Low-Rise Living is home to mostly middle-aged, ethnically diverse singles and single parents. Unlike their low income peers, they rank above average in their use of technology - perhaps influenced by their urban, fast-paced environment.",
      "lifestyle_trait4": "Follows pro boxing",
      "lifestyle_trait5": "Flies JetBlue",
      "segment_social_group": "03",
      "lifestyle_trait6": "Watches Telemundo",
      "style": "moduleBtn1",
      "lifestyle_trait7": "Listens to Jazz",
      "social_group_rank": 13,
      "hh_ipa_class": "Below Avg",
      "hh_age_range": "Age <55",
      "lifestage_group_alias": "Y3",
      "social_group_alias": "U3"
  }
""" 
