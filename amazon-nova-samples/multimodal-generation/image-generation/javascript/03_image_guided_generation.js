import { BedrockImageGenerator } from './BedrockImageGenerator.js';
import { imageToBase64 } from './fileUtils.js';

const conditioningImagePath = "../images/condition-image-1.png";

const generateImages = async () => {
    // Format timestamp for unique directory naming
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const outputDirectory = `output/${timestamp}`;

    const generator = new BedrockImageGenerator({ outputDirectory });

    try {
        // Read image from file and encode it as base64 string
        const conditionImage = await imageToBase64(conditioningImagePath)

        const params = {
            taskType: 'TEXT_IMAGE',
            textToImageParams: {
                text: '3d animated film style, a woman with a crazy blond hair style, wearing a green sequin dress',
                conditionImage: conditionImage,
                controlMode: "SEGMENTATION", // "CANNY_EDGE" or "SEGMENTATION"
                controlStrength: 0.3 // How closely to match the condition image
            },
            imageGenerationConfig: {
                numberOfImages: 1, // Number of variations to generate. 1 to 5.      
                quality: 'standard', // Allowed values are "standard" and "premium"
                width: 1280, // See README for supported output resolutions
                height: 720, // See README for supported output resolutions
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