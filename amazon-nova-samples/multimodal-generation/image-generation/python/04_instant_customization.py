#!/usr/bin/env python3

from random import randint
from amazon_image_gen import BedrockImageGenerator
import file_utils
import logging
import base64
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def main():
    reference_image_paths = [
        "../images/redhair-boy-1.png",
        "../images/redhair-boy-2.png",
        "../images/redhair-boy-3.png",
    ]

    # Load all reference images as base64.
    images = []
    for path in reference_image_paths:
        with open(path, "rb") as image_file:
            images.append(base64.b64encode(image_file.read()).decode("utf-8"))

    # Configure the inference parameters.
    inference_params = {
        "taskType": "IMAGE_VARIATION",
        "imageVariationParams": {
            "images": images, # Images to use as reference
            "text": "a red haired boy sits in a school classroom looking bored, illustrated story", 
            "negativeText": "soccer ball, ball",
            "similarityStrength": 0.9,  # Range: 0.2 to 1.0
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,  # Number of variations to generate. 1 to 5.
            "quality": "standard",  # Allowed values are "standard" and "premium"
            "width": 1280,  # See README for supported output resolutions
            "height": 720,  # See README for supported output resolutions
            "cfgScale": 4.0,  # How closely the prompt will be followed
            "seed": randint(0, 858993459),  # Use a random seed
        },
    }

    # Define an output directory with a unique name.
    generation_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_directory = f"output/{generation_id}"

    # Create the generator.
    generator = BedrockImageGenerator(
        output_directory=output_directory
    )

    # Generate the image(s).
    response = generator.generate_images(inference_params)

    if "images" in response:
        # Save each image
        file_utils.save_base64_images(response["images"], output_directory, "image")

if __name__ == "__main__":
    main()