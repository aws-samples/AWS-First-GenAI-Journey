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
    # The image to be edited.
    source_image_path = "../images/three_pots.jpg"

    # IMPORTANT: The mask must be in PNG format and must contain only pure black and pure white pixels.
    mask_image_path = "../images/three_pots-add_mask.png"

    # Load the input image from disk.
    with open(source_image_path, "rb") as image_file:
        source_image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    # Load the mask image from disk.
    with open(mask_image_path, "rb") as mask_file:
        mask_image_base64 = base64.b64encode(mask_file.read()).decode("utf-8")

    # Configure the inference parameters.
    inference_params = {
        "taskType": "INPAINTING",
        "inPaintingParams": {
            "image": source_image_base64,
            "maskImage": mask_image_base64,
            "text": "a garden gnome",  # The thing to add using the mask.
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,  # Number of variations to generate. 1 to 5.
            "quality": "standard",  # Allowed values are "standard" and "premium"
            "cfgScale": 6.0,  # How closely the prompt will be followed
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