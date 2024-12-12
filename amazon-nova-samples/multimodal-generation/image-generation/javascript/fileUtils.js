import { promises as fs } from 'fs';
import { join } from 'path';
import sharp from 'sharp';

/**
 * Saves a Sharp image object to a specified output directory with a suffix.
 * 
 * @param {sharp.Sharp} image - The Sharp image object to be saved
 * @param {string} outputDirectory - The directory where the image will be saved
 * @param {string} [baseName="image"] - The base name for the image file
 * @param {string} [suffix="_1"] - A suffix to be added to the filename
 * @returns {Promise<void>}
 */
async function saveImage(image, outputDirectory, baseName = "image", suffix = "_1") {
    try {
        // Create directory if it doesn't exist
        await fs.mkdir(outputDirectory, { recursive: true });

        const fileName = `${baseName}${suffix}.png`;
        const filePath = join(outputDirectory, fileName);

        // Save the image as PNG
        await image.toFile(filePath);
    } catch (error) {
        console.error('Error saving image:', error);
        throw error;
    }
}

/**
 * Saves a base64 encoded image to a specified output directory with a suffix.
 * 
 * @param {string} base64Image - The base64 encoded image string
 * @param {string} outputDirectory - The directory where the image will be saved
 * @param {string} [baseName="image"] - The base name for the image file
 * @param {string} [suffix="_1"] - A suffix to be added to the filename
 * @returns {Promise<sharp.Sharp>} A Sharp image object representing the saved image
 */
async function saveBase64Image(base64Image, outputDirectory, baseName = "image", suffix = "_1") {
    // Remove data URL prefix if present
    const base64Data = base64Image.replace(/^data:image\/\w+;base64,/, "");

    // Convert base64 to buffer
    const imageBuffer = Buffer.from(base64Data, 'base64');

    // Create Sharp instance
    const image = sharp(imageBuffer);

    // Save the image
    await saveImage(image, outputDirectory, baseName, suffix);

    return image;
}

/**
 * Saves a list of base64 encoded images to a specified output directory.
 * 
 * @param {string[]} base64Images - An array of base64 encoded image strings
 * @param {string} outputDirectory - The directory where the images will be saved
 * @param {string} [baseName="image"] - The base name for the image files
 * @returns {Promise<sharp.Sharp[]>} An array of Sharp image objects representing the saved images
 */
async function saveBase64Images(base64Images, outputDirectory, baseName = "image") {
    const images = [];

    for (let i = 0; i < base64Images.length; i++) {
        const image = await saveBase64Image(
            base64Images[i],
            outputDirectory,
            baseName,
            `_${i + 1}`
        );
        images.push(image);
    }

    return images;
}

/**
 * Reads an image file and converts it to a base64 string
 * @param {string} filePath - Path to the image file
 * @returns {Promise<string>} Base64 encoded string of the image
 */
const imageToBase64 = async (filePath) => {
    try {
      // Read the file as a buffer
      const imageBuffer = await fs.readFile(filePath);
      
      // Convert buffer to base64 string
      const base64String = imageBuffer.toString('base64');
      
      return base64String;
    } catch (err) {
      throw new Error(`Failed to convert image to base64: ${err.message}`);
    }
  };

export {
    saveBase64Image,
    saveImage,
    saveBase64Images,
    imageToBase64
};