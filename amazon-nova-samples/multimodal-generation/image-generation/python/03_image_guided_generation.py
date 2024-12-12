#!/usr/bin/env python3

from random import randint
from amazon_image_gen import BedrockImageGenerator
import file_utils
import logging
import base64
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    conditioning_image_path = "../images/condition-image-1.png"

    # Read image from file and encode it as base64 string.
    with open(conditioning_image_path, "rb") as image_file:
        condition_image = base64.b64encode(image_file.read()).decode("utf8")

    # Configure the inference parameters.
    inference_params = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": "3d animated film style, a woman with a crazy blond hair style, wearing a green sequin dress",
            "conditionImage": condition_image,
            "controlMode": "SEGMENTATION",  # "CANNY_EDGE" or "SEGMENTATION",
            "controlStrength": 0.3,  # How closely to match the condition image
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
