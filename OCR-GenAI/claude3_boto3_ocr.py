#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# vim: tabstop=2 shiftwidth=2 softtabstop=2 expandtab

import base64
import json
import os

import boto3


MODEL_ID = os.environ.get('MODEL_ID', 'anthropic.claude-sonnet-4-6')


def build_chain():
  region_name = boto3.Session().region_name
  client = boto3.client('bedrock-runtime', region_name=region_name)
  return client


def run_chain(chain, base64_image):
  message_mm = [
    {
      "role": "user",
      "content": [
        {
          "type": "image",
           "source": {
             "type": "base64",
             "media_type": "image/jpeg",
             "data": base64_image
           }
        },
        {
          "type": "text",
          "text": "Extract all text from the image and separate each line or text segment with a newline character."
        }
      ]
    }
  ]

  model_kwargs = {
    'max_tokens': 2000,
    'temperature': 0,
    'top_p': 0.999,
    'top_k': 250,
  }

  body = json.dumps({
      "anthropic_version": "bedrock-2023-05-31",
      "messages": message_mm,
      **model_kwargs
    }
  )

  model_id = MODEL_ID
  response = chain.invoke_model(body=body, modelId=model_id)
  response_body = json.loads(response.get('body').read())
  if response_body['stop_reason'] == 'end_turn':
    text = response_body['content'][0]['text']
    #XXX: For more information, see https://github.com/streamlit/streamlit/issues/868
    return '  \n'.join(text.split('\n'))
  else:
    return f"ERROR: {response_body['stop_reason']}"


if __name__ == "__main__":
  import sys


  def _encode_image(image_path):
    """Getting the base64 string"""
    with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode("utf-8")

  image_path = sys.argv[1]
  base64_image = _encode_image(image_path)

  chain = build_chain()
  result = run_chain(chain, base64_image)
  print(result)
