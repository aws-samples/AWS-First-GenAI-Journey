#!/usr/bin/env python3

from random import randint
from amazon_image_gen import BedrockImageGenerator
import file_utils
import logging
from datetime import datetime
import base64

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    # Load the reference image and encode it as a Base64 string.
    reference_image_path = "../images/color-guided-ref-image-1.png"
    with open(reference_image_path, "rb") as image_file:
        reference_image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    # Configure the inference parameters.
    inference_params = {
        "taskType": "COLOR_GUIDED_GENERATION",
        "colorGuidedGenerationParams": {
            "text": "digital painting of a girl, dreamy and ethereal",
            "colors": ["#81FC81", "#386739", "#C9D688", "#FFFFFF", "#FFFFFF"],
            "referenceImage": reference_image_base64,
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,  # Number of variations to generate. 1 to 5.
            "quality": "standard",  # Allowed values are "standard" and "premium"
            "width": 1280,  # See README for supported output resolutions
            "height": 720,  # See README for supported output resolutions
            "cfgScale": 8.0,  # How closely the prompt will be followed
            "seed": randint(0, 858993459),  # Use a random seed
        },
    }

    # Define an output directory with a unique name.
    generation_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_directory = f"output/{generation_id}"

    # Create the generator.
    generator = BedrockImageGenerator(output_directory=output_directory)

    # Generate the image(s).
    response = generator.generate_images(inference_params)

    if "images" in response:
        # Save each image
        file_utils.save_base64_images(response["images"], output_directory, "image")


if __name__ == "__main__":
    main()
