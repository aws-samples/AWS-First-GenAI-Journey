import { BedrockImageGenerator } from './BedrockImageGenerator.js';
import { imageToBase64 } from './fileUtils.js';

const referenceImagePaths = [
    "../images/redhair-boy-1.png",
    "../images/redhair-boy-2.png",
    "../images/redhair-boy-3.png",
];

const generateImages = async () => {
    // Format timestamp for unique directory naming
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const outputDirectory = `output/${timestamp}`;

    const generator = new BedrockImageGenerator({ outputDirectory });

    try {
        // Read the images from file and encode them as base64 strings
        const referenceImages = await Promise.all(
            referenceImagePaths.map(path => imageToBase64(path))
        );

        const params = {
            taskType: 'IMAGE_VARIATION',
            imageVariationParams: {
                text: 'a red haired boy sits in a school classroom looking bored, illustrated story',
                images: referenceImages,
                negativeText: "soccer ball, ball",
                similarityStrength: 0.9,  // Range: 0.2 to 1.0
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