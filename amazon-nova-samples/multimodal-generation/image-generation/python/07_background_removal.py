#!/usr/bin/env python3

from amazon_image_gen import BedrockImageGenerator
import file_utils
import logging
import base64
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def main():
    # The image to be edited.
    source_image_path = "../images/man-in-orange.png"

    # Read image from disk.
    with open(source_image_path, "rb") as image_file:
        source_image_base64 = base64.b64encode(image_file.read()).decode("utf8")

    # Configure the inference parameters.
    inference_params = {
        "taskType": "BACKGROUND_REMOVAL",
        "backgroundRemovalParams": {
            "image": source_image_base64,
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