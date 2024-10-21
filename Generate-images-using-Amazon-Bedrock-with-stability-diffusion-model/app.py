import streamlit as st
import boto3
import json
import base64
import io
from PIL import Image

# Initialize the Bedrock Runtime client
client = boto3.client('bedrock-runtime', region_name='us-west-2')

# Set page configuration for a professional look
st.set_page_config(
    page_title="AWS Bedrock Image Generator",
    page_icon="🖼️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Main app container
st.title('AWS Bedrock Image Generator')
st.subheader("Create stunning images with a simple text prompt!")

st.write("""
    This application uses **Stable Diffusion** models from Stability AI to generate images based on your input.
    Simply enter a descriptive prompt, select your options, and click the 'Generate Image' button to see the results.
""")

# Sidebar for instructions and settings
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

# Dropdown for model selection
model_choice = st.selectbox(
    "Select Stable Diffusion Model:",
    options=[
        'stability.stable-diffusion-xl-v1',
        'stability.stable-diffusion-xl-v0',
        'stability.sd3-large-v1:0',
        'stability.stable-image-ultra-v1:0',
        'stability.stable-image-core-v1:0'
    ],
    format_func=lambda x: {
        'stability.stable-diffusion-xl-v0': 'Stable Diffusion XL 0.x',
        'stability.stable-diffusion-xl-v1': 'Stable Diffusion XL 1.x',
        'stability.sd3-large-v1:0': 'Stable Diffusion 3 Large 1.x',
        'stability.stable-image-ultra-v1:0': 'Stable Image Ultra 1.x',
        'stability.stable-image-core-v1:0': 'Stability Image Core 1.x'
    }.get(x, x)
)

# User input for the image generation prompt
prompt = st.text_input(
    'Enter your prompt for image generation:',
    value='A landscape painting of mountains during sunrise.',
    help="Describe the image you want to generate. Include 'portrait' or 'landscape' to influence orientation."
)

# New feature: Negative prompt input
negative_prompt = st.text_area(
    'Add negative prompt (Optional):',
    value='',
    help="Specify what you don't want in the image. For example: 'no watermarks, no text'."
)

# Option to select image orientation
orientation = st.radio(
    "Choose Image Orientation:",
    options=['16:9 (Landscape)', '9:16 (Portrait)'],
    index=0
)

# Map orientation to aspect_ratio
aspect_ratio = '16:9' if 'Landscape' in orientation else '9:16'

# New section: Advanced configurations
st.subheader("Advanced configurations")

generation_steps = st.slider(
    "Generation Steps:",
    min_value=10,
    max_value=100,
    value=50,
    help="Define the number of steps the model takes to generate the image (higher values may improve detail)."
)

seed = st.number_input(
    "Seed (Optional):",
    min_value=0,
    value=0,
    help="Use a seed to control image reproducibility. Leave as 0 for random generation."
)

# Option to select number of images
num_images = st.selectbox(
    "How many images would you like to generate?",
    options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    help="Choose the number of images to generate (1-10)."
)

# Button to generate the images
if st.button('Generate Image'):
    with st.spinner('Generating image(s), please wait...'):
        try:
            images_generated = False
            for i in range(num_images):
                # Define the request body for Bedrock API
                body = {
                    'prompt': prompt,
                    'negative_prompt': negative_prompt,
                    'aspect_ratio': aspect_ratio,
                    'output_format': 'png'
                }
                
                # Only include the seed if it's not 0
                if seed != 0:
                    body['seed'] = seed

                # Convert the body to JSON
                body_json = json.dumps(body)

                # Invoke the Bedrock model
                response = client.invoke_model(
                    modelId=model_choice,
                    body=body_json
                )

                # Decode the response and fetch the image data
                response_body = response['body'].read().decode('utf-8')
                output_body = json.loads(response_body)
                base64_image = output_body.get("images", [None])[0]

                # Check if image was successfully generated
                if base64_image:
                    images_generated = True
                    # Convert the base64-encoded image to an actual image
                    image_data = base64.b64decode(base64_image)
                    image = Image.open(io.BytesIO(image_data))

                    # Display the image with caption and download option
                    st.image(image, caption=f'Generated Image {i + 1}', use_column_width=True)

                    # Create an in-memory buffer for download
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    buf.seek(0)

                    # Download button for each image
                    st.download_button(
                        label=f"Download Image {i + 1}",
                        data=buf,
                        file_name=f"generated_image_{i + 1}.png",
                        mime="image/png"
                    )
                else:
                    st.warning(f"Image {i + 1} was not generated. Skipping to the next image.")

            if not images_generated:
                st.error("No images were generated. Please try a different prompt.")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer section for branding or credits
st.write("___")
st.markdown(
    """
    Powered by [AWS Bedrock](https://aws.amazon.com/bedrock/) | Created with ❤️ by **Kha Van**
    """
)
