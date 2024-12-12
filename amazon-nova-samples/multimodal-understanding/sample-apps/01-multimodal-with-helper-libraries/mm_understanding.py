import base64
import boto3
import os
import streamlit as st
import warnings
import utils

from sagemaker.session import Session

warnings.filterwarnings("ignore")

LITE_MODEL_ID = "us.amazon.nova-lite-v1:0"


is_video = False
media_input = None
media_extension = None
model_id = LITE_MODEL_ID
bucket_name = Session().default_bucket()
system_prompt = "You are an expert video understanding chatbot. You will be shown a video alongside a user input and must provide a clear and concise answer to the question from the user. You must answer any follow up questions in a helpful manner"

models = [
    "us.amazon.nova-lite-v1:0",
    "us.amazon.nova-pro-v1:0",
    "us.anthropic.claude-3-haiku-20240307-v1:0",
]

video_input_models = ["us.amazon.nova-lite-v1:0", "us.amazon.nova-pro-v1:0"]

image_input_models = [
    "us.amazon.nova-lite-v1:0",
    "us.amazon.nova-pro-v1:0",
    "us.anthropic.claude-3-haiku-20240307-v1:0",
]

with st.sidebar:
    # = st.text_area("System Prompt", key='chatbot_system_prompt')
    max_new_tokens = st.number_input(
        "Max New Tokens", value=1024, key="chatbot_max_new_tokens"
    )
    temperature = st.number_input("Temperature", value=0.0, key="chatbot_temperature")
    top_p = st.number_input("Top P", value=1.0, key="chatbot_top_p")
    top_k = st.number_input("Top K", value=250, key="chatbot_top_k")
    model_id = st.selectbox("Model", models, key="chatbot_model_id")
    resample_all_video = st.checkbox(
        "Resample video to images? (Amazon models only)",
        value=False,
        key="resample_all_video",
    )

st.title("Multimodal Understanding with Amazon models")

description = """
This demo Streamlit application showcases how the Amazon models are able to understand and answer questions about videos and images.

You can upload a video or image and ask the model questions.
"""
st.text(description)

uploaded_file = st.file_uploader(
    "Upload a photo or a video", type=["mp4", "png", "jpg"]
)

if uploaded_file is not None:
    data_bytes = uploaded_file.read()
    file_name = uploaded_file.name

    is_video = file_name.endswith(".mp4")

    if file_name.endswith(".mp4"):
        media_extension = "mp4"
    elif file_name.endswith(".png"):
        media_extension = "png"
    else:
        media_extension = "jpeg"

    base_64_encoded_data = base64.b64encode(data_bytes)
    media_input = data_bytes

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.display_messages = []

for msg in st.session_state.display_messages:
    if "caption" in msg.keys():
        st.caption(msg["caption"])
        continue
    for content in msg["content"]:
        if "video" in content:
            st.chat_message(msg["role"]).video(content["video"]["source"]["bytes"])
        elif "image" in content:
            st.chat_message(msg["role"]).image(content["image"]["source"]["bytes"])
        elif "text" in content:
            st.chat_message(msg["role"]).write(content["text"])


if prompt := st.chat_input():
    client = boto3.client("bedrock-runtime")
    if is_video and media_input and len(st.session_state.messages) == 0:

        if model_id in video_input_models and not resample_all_video:
            media_input_s3 = utils.resize_video(media_input, bucket_name)
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": [
                        {"text": prompt},
                        {
                            "video": {
                                "format": media_extension,
                                "source": {
                                    "s3Location": {
                                        "uri": media_input_s3,
                                        "bucketOwner": boto3.client("sts")
                                        .get_caller_identity()
                                        .get("Account"),
                                    }
                                },
                            }
                        },
                    ],
                }
            )

            st.session_state.display_messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "video": {
                                "format": "mp4",
                                "source": {"bytes": media_input},
                            }
                        },
                        {"text": prompt},
                    ],
                }
            )
            duration, frame_count, fps = utils.get_video_info(media_input)

            st.session_state.display_messages.append(
                {
                    "type": "caption",
                    "caption": f"Duration: {duration} seconds. Frame Count: {frame_count}. {fps} FPS",
                }
            )
            st.session_state.display_messages.append(
                {
                    "type": "caption",
                    "caption": f"Sampled Frame Count: {utils.get_sampled_frame_count(duration)}. Sampled FPS: {utils.get_sampled_fps(duration)}. Token Count: {utils.get_sampled_tokens(duration)}",
                }
            )

            st.caption(
                f"Duration: {duration} seconds. Frame Count: {frame_count}. {fps} FPS"
            )
            st.caption(
                f"Sampled Frame Count: {utils.get_sampled_frame_count(duration)}. Sampled FPS: {utils.get_sampled_fps(duration)}. Token Count: {utils.get_sampled_tokens(duration)}"
            )

        elif is_video and resample_all_video or model_id in image_input_models:
            video_as_frames = utils.resample_video_to_frames(media_input)
            frames_as_bytes = utils.convert_frames_to_converse_format(video_as_frames)

            content = [
                {"image": {"format": "jpeg", "source": {"bytes": frame_bytes}}}
                for frame_bytes in frames_as_bytes
            ]
            content.append({"text": prompt})

            st.session_state.messages.append({"role": "user", "content": content})
            st.session_state.display_messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "video": {
                                "format": "mp4",
                                "source": {"bytes": media_input},
                            }
                        },
                        {"text": prompt},
                    ],
                }
            )
        else:  # Model doesn't support image or video
            st.session_state.messages.append(
                {"role": "user", "content": [{"text": prompt}]}
            )

            st.session_state.display_messages.append(
                {"role": "user", "content": [{"text": prompt}]}
            )
            st.session_state.display_messages.append(
                {
                    "type": "caption",
                    "caption": f"{model_id} doesn't support visual input.",
                }
            )

        st.chat_message("user").video(media_input)

        st.chat_message("user").write(prompt)
    elif media_input and not is_video:  # Media is uploaded and it is an image
        st.session_state.messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": media_extension,
                            "source": {"bytes": media_input},
                        }
                    }
                ],
            }
        )
        st.session_state.display_messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "image": {
                            "format": media_extension,
                            "source": {"bytes": media_input},
                        }
                    },
                    {"text": prompt},
                ],
            }
        )
    else:
        st.session_state.messages.append(
            {"role": "user", "content": [{"text": prompt}]}
        )
        st.session_state.display_messages.append(
            {"role": "user", "content": [{"text": prompt}]}
        )
        st.chat_message("user").write(prompt)

    inf_params = {
        "maxTokens": max_new_tokens,
        "temperature": temperature,
        "topP": top_p,
    }

    response2 = client.converse_stream(
        modelId=model_id,
        messages=st.session_state.messages,
        inferenceConfig=inf_params,
        system=[{"text": system_prompt}],
    )

    stream = response2["stream"]
    usage = {}
    output = st.write_stream(utils.parse_stream_converse(stream, usage))
    msg = output

    model_usage = usage
    st.session_state.messages.append({"role": "assistant", "content": [{"text": msg}]})
    st.session_state.display_messages.append(
        {"role": "assistant", "content": [{"text": msg}]}
    )
    st.caption(
        f"Input tokens: {model_usage['usage']['inputTokens']}. Output Tokens: {model_usage['usage']['outputTokens']}."
    )
    st.session_state.display_messages.append(
        {
            "type": "caption",
            "caption": f"Input tokens: {model_usage['usage']['inputTokens']}. Output Tokens: {model_usage['usage']['outputTokens']}.",
        }
    )
