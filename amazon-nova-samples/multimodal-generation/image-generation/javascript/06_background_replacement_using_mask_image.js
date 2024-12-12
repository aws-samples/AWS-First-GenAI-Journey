import { BedrockImageGenerator } from './BedrockImageGenerator.js';
import { imageToBase64 } from './fileUtils.js';

// Path to image to be edited
const sourceImagePath = "../images/three_pots.jpg";

// Set the image to be used as a mask. IMPORTANT: The mask must be in PNG format and must contain only pure
// black and pure white pixels.
const maskImagePath = "../images/three_pots-center_pot_mask.png";

const generateImages = async () => {
    // Format timestamp for unique directory naming
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const outputDirectory = `output/${timestamp}`;

    const generator = new BedrockImageGenerator({ outputDirectory });

    try {
        // Read the images from file and encode them as base64 strings
        const sourceImage = await imageToBase64(sourceImagePath);
        const maskImage = await imageToBase64(maskImagePath);

        const params = {
            taskType: 'OUTPAINTING',
            outPaintingParams: {
                image: sourceImage,
                maskImage: maskImage,
                text: "potted flower sitting on a picnic table, backyard wedding decorations, beautiful, highest quality", // Description of the background to generate
                outPaintingMode: "PRECISE",  // "DEFAULT" softens the mask. "PRECISE" keeps it sharp.
            },
            imageGenerationConfig: {
                numberOfImages: 1, // Number of variations to generate. 1 to 5.      
                quality: 'standard', // Allowed values are "standard" and "premium"
                cfgScale: 7.0, // How closely the prompt will be followed
                seed: Math.floor(Math.random() * 858993459), // Use a random seed
            }
        };

        const images = await generator.generateImages(params);
        console.log('Generated images:', images.join(', '));
    } catch (err) {
        console.error('Image generation failed:', err.message);
        process.exit(1);
    }
};

// Self-executing async function
(async () => {
    try {
        await generateImages();
    } catch (err) {
        console.error('Fatal error:', err.message);
        process.exit(1);
    }
})();