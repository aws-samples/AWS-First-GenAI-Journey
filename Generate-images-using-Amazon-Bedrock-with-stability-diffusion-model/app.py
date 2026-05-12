import os
import sys
import json
import base64
import io
from dataclasses import dataclass

import streamlit as st
import boto3
import botocore.config
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.security_utils import sanitize_input


@dataclass(frozen=True)
class ImageGenConfig:
    region: str = os.environ.get("AWS_REGION", "us-west-2")
    guardrail_id: str = os.environ.get("BEDROCK_GUARDRAIL_ID", "")
    guardrail_version: str = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT")


CFG = ImageGenConfig()

_boto_config = botocore.config.Config(read_timeout=120)
client = boto3.client("bedrock-runtime", region_name=CFG.region, config=_boto_config)

st.set_page_config(
    page_title="AWS Bedrock Image Generator",
    page_icon="🖼️",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("AWS Bedrock Image Generator")
st.subheader("Create stunning images with a simple text prompt!")

st.write("""
    This application uses **Stable Diffusion** models from Stability AI to generate images based on your input.
    Simply enter a descriptive prompt, select your options, and click the 'Generate Image' button to see the results.
""")

with st.sidebar:
    st.header("Instructions")
    st.write("""
    1. Enter a creative prompt that describes the image you want to generate.
    2. Select the desired model and number of images.
    3. Choose advanced options such as image orientation, size, and seed.
    4. Click **Generate Image** and wait for the images to appear.
    5. Download your images using the download links below each image.
    """)
    st.write("Example prompt: *A landscape painting of mountains during sunrise*")

model_choice = st.selectbox(
    "Select Stable Diffusion Model:",
    options=[
        "stability.stable-diffusion-xl-v1",
        "stability.stable-diffusion-xl-v0",
        "stability.sd3-large-v1:0",
        "stability.stable-image-ultra-v1:0",
        "stability.stable-image-core-v1:0",
    ],
    format_func=lambda x: {
        "stability.stable-diffusion-xl-v0": "Stable Diffusion XL 0.x",
        "stability.stable-diffusion-xl-v1": "Stable Diffusion XL 1.x",
        "stability.sd3-large-v1:0": "Stable Diffusion 3 Large 1.x",
        "stability.stable-image-ultra-v1:0": "Stable Image Ultra 1.x",
        "stability.stable-image-core-v1:0": "Stability Image Core 1.x",
    }.get(x, x),
)

prompt = st.text_input(
    "Enter your prompt for image generation:",
    value="A landscape painting of mountains during sunrise.",
    help="Describe the image you want to generate.",
)

negative_prompt = st.text_area(
    "Add negative prompt (Optional):",
    value="",
    help="Specify what you don't want in the image.",
)

orientation = st.radio(
    "Choose Image Orientation:",
    options=["16:9 (Landscape)", "9:16 (Portrait)"],
    index=0,
)

aspect_ratio = "16:9" if "Landscape" in orientation else "9:16"

st.subheader("Advanced configurations")

generation_steps = st.slider(
    "Generation Steps:", min_value=10, max_value=100, value=50,
    help="Number of steps the model takes to generate the image.",
)

seed = st.number_input(
    "Seed (Optional):", min_value=0, value=0,
    help="Use a seed to control image reproducibility. 0 for random.",
)

num_images = st.selectbox(
    "How many images would you like to generate?",
    options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
)

if st.button("Generate Image"):
    with st.spinner("Generating image(s), please wait..."):
        try:
            sanitized_prompt: str = sanitize_input(prompt)
            sanitized_negative: str = sanitize_input(negative_prompt)
            images_generated = False

            for i in range(num_images):
                body: dict = {
                    "prompt": sanitized_prompt,
                    "negative_prompt": sanitized_negative,
                    "aspect_ratio": aspect_ratio,
                    "output_format": "png",
                }
                if seed != 0:
                    body["seed"] = seed

                response = client.invoke_model(
                    modelId=model_choice,
                    body=json.dumps(body),
                )

                response_body = json.loads(response["body"].read().decode("utf-8"))
                base64_image = response_body.get("images", [None])[0]

                if base64_image:
                    images_generated = True
                    image_data = base64.b64decode(base64_image)
                    image = Image.open(io.BytesIO(image_data))
                    st.image(image, caption=f"Generated Image {i + 1}", use_column_width=True)

                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    buf.seek(0)
                    st.download_button(
                        label=f"Download Image {i + 1}",
                        data=buf,
                        file_name=f"generated_image_{i + 1}.png",
                        mime="image/png",
                    )
                else:
                    st.warning(f"Image {i + 1} was not generated. Skipping.")

            if not images_generated:
                st.error("No images were generated. Please try a different prompt.")
        except Exception as e:
            st.error(f"An error occurred: {e!s}")

st.write("___")
st.markdown(
    "Powered by [AWS Bedrock](https://aws.amazon.com/bedrock/) | Created with ❤️ by **Kha Van**"
)
