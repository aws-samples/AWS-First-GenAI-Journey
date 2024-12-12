"""
utils.py

Functions:
- generate_script: Get the dialogue from the LLM.
- call_llm: Call the LLM with the given prompt and dialogue format.
- parse_url: Parse the given URL and return the text content.
- generate_podcast_audio: Generate audio for podcast using TTS or advanced audio models.
- _use_suno_model: Generate advanced audio using Bark.
- _use_melotts_api: Generate audio using TTS model.
- _get_melo_tts_params: Get TTS parameters based on speaker and language.
"""

import io

# Standard library imports
import json
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Union
from urllib.parse import urlparse

import boto3
from botocore.config import Config
import requests
from botocore.exceptions import ClientError
from langchain_aws import ChatBedrockConverse
from pydub import AudioSegment
from pypdf import PdfReader
from scipy.io.wavfile import write as write_wav
from loguru import logger

# Local imports
from constants import (
    AWS_REGION,
    ERROR_MESSAGE_NOT_PDF,
    ERROR_MESSAGE_READING_PDF,
    JINA_READER_URL,
    JINA_RETRY_ATTEMPTS,
    JINA_RETRY_DELAY,
)
from schema import MediumDialogue, ShortDialogue
from prompts import OUTPUT_FORMAT_MODIFIER
import base64


def generate_script(
    model_id: str,
    system_prompt: str,
    input_text: str,
    video_files: list[str] | None,
    output_model: Union[ShortDialogue, MediumDialogue],
) -> Union[ShortDialogue, MediumDialogue]:
    """Get the dialogue from the LLM."""

    # Call the LLM for the first time
    # We only use video for draft generation
    first_draft_dialogue = call_llm(
        model_id, system_prompt, input_text, video_files, output_model
    )
    logger.info(f"First draft dialogue:\n {first_draft_dialogue}")
    # Call the LLM a second time to improve the dialogue
    system_prompt_with_dialogue = f"{system_prompt}\n\nHere is the first draft of the dialogue you provided:\n\n{first_draft_dialogue.model_dump_json()}."
    final_dialogue = call_llm(
        model_id,
        system_prompt_with_dialogue,
        "Please improve the dialogue. Make it more natural and engaging.\n"
        + OUTPUT_FORMAT_MODIFIER,
        None,
        output_model,
    )
    logger.info(f"Final dialogue:\n {final_dialogue}")

    return final_dialogue


def get_pdf_from_s3(object_url: str) -> BytesIO:
    """
    Retrieves a PDF file from S3 and returns it as a BytesIO object

    Args:
        bucket_name (str): Name of the S3 bucket
        key_name (str): Key/path of the PDF file in the bucket

    Returns:
        BytesIO: PDF file contents as a BytesIO object

    Raises:
        ClientError: If there's an error retrieving the file from S3
    """
    try:

        # Create an S3 client
        s3_client = boto3.client("s3")

        parsed_url = urlparse(object_url)
        bucket_name = parsed_url.netloc.split(".")[0]
        key_name = parsed_url.path.lstrip("/")

        # Get the PDF file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=key_name)

        # Read the file content
        pdf_content = response["Body"].read()

        # Create a BytesIO object
        pdf_file = BytesIO(pdf_content)

        text = read_pdf(pdf_file)

        return text

    except ClientError as e:
        raise Exception(
            f"Error reading PDF file '{key_name}' from bucket '{bucket_name}': {str(e)}"
        )


def read_pdf(file_name: str | bytes):
    text = ""
    try:
        reader = PdfReader(file_name)
        text += "\n\n".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        raise Exception(f"{ERROR_MESSAGE_READING_PDF}: {str(e)}")

    return text


def read_pdfs(files: list[str] | bytes) -> str:
    text = ""

    for file in files:
        if not file.lower().endswith(".pdf"):
            raise Exception(ERROR_MESSAGE_NOT_PDF)

        text += read_pdf(file)

    return text


def call_llm(
    model_id: str,
    system_prompt: str,
    text: str,
    video_files: list[str] | None,
    dialogue_format: Any,
) -> Any:
    logger.info(f"Video files are passed: {video_files}")
    if not video_files:
        result = invoke_bedrock_model(model_id, system_prompt, text, dialogue_format)
    else:

        result = invoke_bedrock_model_video(
            model_id, system_prompt, text, dialogue_format, video_files
        )

    logger.info(f"Result:\n {result}")
    result_output = (
        result["output"]["message"]["content"][0]["text"]
        .split("<output>")[-1]
        .split("</output>")[0]
    )

    scratchpad = (
        result["output"]["message"]["content"][0]["text"]
        .split("<scratchpad>")[-1]
        .split("</scratchpad>")[0]
    )

    idx_start = result_output.find("{")
    idx_end = result_output.rfind("}") + 1

    result_output = result_output[idx_start:idx_end]
    json_result = json.loads(result_output)

    json_result["scratchpad"] = scratchpad

    return dialogue_format.parse_obj(json_result)


def parse_url(url: str) -> str:
    """Parse the given URL and return the text content."""
    for attempt in range(JINA_RETRY_ATTEMPTS):
        try:
            full_url = f"{JINA_READER_URL}{url}"
            response = requests.get(full_url, timeout=60)
            response.raise_for_status()  # Raise an exception for bad status codes
            break
        except requests.RequestException as e:
            if attempt == JINA_RETRY_ATTEMPTS - 1:  # Last attempt
                raise ValueError(
                    f"Failed to fetch URL after {JINA_RETRY_ATTEMPTS} attempts: {e}"
                ) from e
            time.sleep(JINA_RETRY_DELAY)  # Wait for X second before retrying
    return response.text


def text_to_speech(text, voice_id, polly_client):
    """Convert text to speech using Amazon Polly"""
    try:
        response = polly_client.synthesize_speech(
            Text=text,
            OutputFormat="mp3",
            VoiceId=voice_id,
            Engine="generative",
        )
        # Convert the audio stream to AudioSegment
        audio = AudioSegment.from_mp3(io.BytesIO(response["AudioStream"].read()))
        return audio

    except Exception as e:
        print(f"Error synthesizing speech: {str(e)}")
        return None


def create_dialogue_audio(dialogue, output_file):
    """Convert dialogue to speech and save to file"""

    # Initialize Polly client
    polly_client = boto3.Session(
        region_name="us-east-1"  # Change to your preferred region
    ).client("polly")

    # Initialize an empty audio segment
    combined_audio = AudioSegment.empty()

    # Define voices for each speaker
    speaker_voices = {
        "Guest": "Danielle",  # Male voice
        "Host": "Stephen",  # Female voice
    }
    # Process each line of dialogue
    for line in dialogue:
        speaker = line.speaker
        text = line.text
        # Add a small pause between lines
        if len(combined_audio) > 0:
            combined_audio += AudioSegment.silent(duration=500)  # 500ms pause

        # Convert text to speech
        audio_segment = text_to_speech(text, speaker_voices[speaker], polly_client)

        if audio_segment:
            combined_audio += audio_segment

    # Export the combined audio to a file
    combined_audio.export(output_file, format="mp3")


def list_foundation_models(region: str = "us-east-1") -> dict:
    """
    List all available foundation models in Amazon Bedrock

    Returns:
        list: List of model summaries if successful, None if there's an error
    """
    try:
        # Create a Bedrock client
        bedrock_client = boto3.client("bedrock", config=Config(region_name=region))

        # Get the list of foundation models
        response = bedrock_client.list_foundation_models()

        # Extract model summaries from response
        models = response["modelSummaries"]

        return {item["modelName"]: item["modelId"] for item in models}

    except ClientError as e:
        raise


def invoke_bedrock_model(
    model_id: str, system_prompt: str, text: str, dialogue_format: Any
) -> Any:

    logger.info(f"Calling LLM {model_id}")

    messages = [{"role": "user", "content": [{"text": text}]}]

    session = boto3.Session(
        region_name=AWS_REGION,
    )

    bedrock_runtime_client = session.client("bedrock-runtime")

    n_tries = 0
    result = ""
    while True:
        if n_tries > 2:
            raise Exception("Too many retries")
        try:

            result = bedrock_runtime_client.converse(
                modelId=model_id,
                messages=messages,
                system=[{"text": system_prompt}],
                inferenceConfig={"temperature": 0.2},
            )

            break
        except ClientError as e:
            logger.info(f"Exception {e}")
            if e.response["Error"]["Code"] == "ThrottlingException":
                logger.info("Throttling!. Will Sleep for 90 seconds")
                n_tries += 1
                if n_tries > 2:
                    raise e
                time.sleep(90)
            else:
                raise e
        except Exception as ex:
            logger.info(f"Exception {ex}")
            raise ex

        n_tries += 1

    return result


def invoke_bedrock_model_video(
    model_id: str,
    system_prompt: str,
    text: str,
    dialogue_format: Any,
    video_files: list[str],
) -> Any:

    logger.info(f"Calling LLM with video {model_id}")

    video_data = video_to_base64_string(video_files)
    video_messages = [
        {
            "role": "user",
            "content": [
                {
                    "video": {
                        "format": "mp4",
                        "source": {"bytes": data},
                    }
                }
            ],
        }
        for data in video_data
    ]

    text_message = {"role": "user", "content": [{"text": text}]}

    video_messages.append(text_message)
    # logger.info(video_messages)
    session = boto3.Session(
        region_name=AWS_REGION,
    )

    bedrock_runtime_client = session.client("bedrock-runtime")
    native_request = {
        # "schemaVersion": "messages-v1",
        "messages": video_messages,
        "system": [{"type": "system", "content": [{"text": system_prompt}]}],
        # "inferenceConfig": inf_params,
    }
    n_tries = 0
    result = ""
    while True:
        if n_tries > 2:
            raise Exception("Too many retries")
        try:

            # result = bedrock_runtime_client.converse(
            #     modelId=model_id,
            #     messages=messages,
            #     system=[{"text": system_prompt}],
            #     inferenceConfig={"temperature": 0.2},
            # )
            response = bedrock_runtime_client.invoke_model(
                modelId=model_id, body=json.dumps(native_request)
            )
            result = json.loads(response["body"].read())

            logger.info(result)
            # model_response = json.loads(response["body"].read())

            break
        except ClientError as e:
            logger.info(f"Exception {e}")
            if e.response["Error"]["Code"] == "ThrottlingException":
                logger.info("Throttling!. Will Sleep for 90 seconds")
                n_tries += 1
                if n_tries > 2:
                    raise e
                time.sleep(90)
            else:
                raise e
        except Exception as ex:
            logger.info(f"Exception {ex}")
            raise ex

        n_tries += 1

    return result


def video_to_base64_string(files: list[str]):
    base64_strings = []
    for file_path in files:
        with open(file_path, "rb") as file:
            base64_string = base64.b64encode(file.read()).decode("utf-8")
            base64_strings.append(base64_string)
    return base64_strings
