import { BedrockImageGenerator } from './BedrockImageGenerator.js';
import { imageToBase64 } from './fileUtils.js';

// Path to image to be edited
const sourceImagePath = "../images/three_pots.jpg";

const generateImages = async () => {
    // Format timestamp for unique directory naming
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const outputDirectory = `output/${timestamp}`;

    const generator = new BedrockImageGenerator({ outputDirectory });

    try {
        // Read the images from file and encode them as base64 strings
        const sourceImage = await imageToBase64(sourceImagePath);

        const params = {
            taskType: 'INPAINTING',
            inPaintingParams: {
                image: sourceImage,
                maskPrompt: "flowers in pots", // Description of the elements to replace
                text: "garden gnome statues on a table"
            },
            imageGenerationConfig: {
                numberOfImages: 1, // Number of variations to generate. 1 to 5.      
                quality: 'standard', // Allowed values are "standard" and "premium"
                cfgScale: 8.0, // How closely the prompt will be followed
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