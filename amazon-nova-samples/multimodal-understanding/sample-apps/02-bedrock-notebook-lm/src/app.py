"""
main.py
"""

# Standard library imports
import base64
import glob
import os
import random
import time
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Optional, Tuple

# Third-party imports
import gradio as gr
from pydub import AudioSegment
from pypdf import PdfReader

# Local imports
from constants import (
    APP_TITLE,
    AWS_REGION,
    CHARACTER_LIMIT,
    ERROR_MESSAGE_NO_INPUT,
    ERROR_MESSAGE_TOO_LONG,
    UI_ALLOW_FLAGGING,
    UI_API_NAME,
    UI_CACHE_EXAMPLES,
    UI_CONCURRENCY_LIMIT,
    UI_DESCRIPTION,
    UI_INPUTS,
    UI_OUTPUTS,
    UI_SHOW_API,
)
from prompts import (
    LENGTH_MODIFIERS,
    QUESTION_MODIFIER,
    SYSTEM_PROMPT,
    TONE_MODIFIER,
    OUTPUT_FORMAT_MODIFIER,
)
from schema import MediumDialogue, ShortDialogue
from utils import (
    create_dialogue_audio,
    generate_script,
    get_pdf_from_s3,
    parse_url,
    read_pdfs,
    list_foundation_models,
    video_to_base64_string,
)


def generate_podcast(
    model_name: str,
    video_files: List[str],
    files: List[str],
    url: Optional[str],
    s3_url: Optional[str],
    question: Optional[str],
    tone: Optional[str],
    length: Optional[str],
    # language: str,
) -> Tuple[str, str]:
    """Generate the audio and transcript from the PDFs and/or URL."""

    text = ""

    model_map = list_foundation_models(AWS_REGION)

    model_id = model_map[model_name]

    # Check if at least one input is provided
    if not files and not url and not s3_url and not video_files:
        raise gr.Error(ERROR_MESSAGE_NO_INPUT)

    # Process PDFs if any
    if files:
        text += read_pdfs(files)

    # Process URL if provided
    if url:
        try:
            url_text = parse_url(url)
            text += "\n\n" + url_text
        except ValueError as e:
            raise gr.Error(str(e))

    if s3_url:
        try:
            s3_text = get_pdf_from_s3(s3_url)
            text += "\n\n" + s3_text
        except ValueError as e:
            raise gr.Error(str(e))

    # Check total character count
    if len(text) > CHARACTER_LIMIT:
        raise gr.Error(ERROR_MESSAGE_TOO_LONG)

    # Modify the system prompt based on the user input
    modified_system_prompt = SYSTEM_PROMPT

    if question:
        modified_system_prompt += f"\n\n{QUESTION_MODIFIER} {question}"
    if tone:
        modified_system_prompt += f"\n\n{TONE_MODIFIER} {tone}."
    if length:
        modified_system_prompt += f"\n\n{LENGTH_MODIFIERS[length]}"
    # if language:
    #     modified_system_prompt += f"\n\n{LANGUAGE_MODIFIER} {language}."

    text = f"<text>\n{text}</text>\n" + OUTPUT_FORMAT_MODIFIER

    # Call the LLM
    if length == "Short (1-2 min)":
        llm_output = generate_script(
            model_id, modified_system_prompt, text, video_files, ShortDialogue
        )
    else:
        llm_output = generate_script(
            model_id, modified_system_prompt, text, video_files, MediumDialogue
        )

    # Process the dialogue
    transcript = "\n\n".join(
        [item.speaker + ": " + item.text for item in llm_output.dialogue]
    )

    create_dialogue_audio(llm_output.dialogue, "dialogue_output.mp3")

    return "dialogue_output.mp3", transcript


# with open("logo.svg", "rb") as image_file:
#     encoded_string = base64.b64encode(image_file.read()).decode()


demo = gr.Interface(
    title=APP_TITLE,
    description=UI_DESCRIPTION,
    fn=generate_podcast,
    theme=gr.themes.Monochrome(primary_hue=gr.themes.colors.orange),
    inputs=[
        gr.Dropdown(
            label=UI_INPUTS["models"]["label"],  # Step 4: Tone
            choices=list(list_foundation_models(AWS_REGION).keys()),
            value=UI_INPUTS["models"]["value"],
        ),
        gr.File(
            label=UI_INPUTS["video_upload"]["label"],  # Step 1: File upload
            file_types=UI_INPUTS["video_upload"]["file_types"],
            file_count=UI_INPUTS["video_upload"]["file_count"],
        ),
        gr.File(
            label=UI_INPUTS["file_upload"]["label"],  # Step 1: File upload
            file_types=UI_INPUTS["file_upload"]["file_types"],
            file_count=UI_INPUTS["file_upload"]["file_count"],
        ),
        gr.Textbox(
            label=UI_INPUTS["url"]["label"],  # Step 2: URL
            placeholder=UI_INPUTS["url"]["placeholder"],
        ),
        gr.Textbox(
            label=UI_INPUTS["s3"]["label"],  # Step 2: URL
            placeholder=UI_INPUTS["s3"]["placeholder"],
        ),
        gr.Textbox(label=UI_INPUTS["question"]["label"]),  # Step 3: Question
        gr.Dropdown(
            label=UI_INPUTS["tone"]["label"],  # Step 4: Tone
            choices=UI_INPUTS["tone"]["choices"],
            value=UI_INPUTS["tone"]["value"],
        ),
        gr.Dropdown(
            label=UI_INPUTS["length"]["label"],  # Step 5: Length
            choices=UI_INPUTS["length"]["choices"],
            value=UI_INPUTS["length"]["value"],
        ),
        # gr.Dropdown(
        #     choices=UI_INPUTS["language"]["choices"],  # Step 6: Language
        #     value=UI_INPUTS["language"]["value"],
        #     label=UI_INPUTS["language"]["label"],
        # )
    ],
    outputs=[
        gr.Audio(
            label=UI_OUTPUTS["audio"]["label"], format=UI_OUTPUTS["audio"]["format"]
        ),
        gr.Markdown(label=UI_OUTPUTS["transcript"]["label"]),
    ],
    allow_flagging=UI_ALLOW_FLAGGING,
    api_name=UI_API_NAME,
    # theme=gr.themes.Ocean(),
    concurrency_limit=UI_CONCURRENCY_LIMIT,
    cache_examples=UI_CACHE_EXAMPLES,
)

if __name__ == "__main__":
    demo.launch(show_api=UI_SHOW_API, server_name="0.0.0.0")
