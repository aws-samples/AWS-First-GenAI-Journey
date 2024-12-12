import { BedrockImageGenerator } from './BedrockImageGenerator.js';
import { imageToBase64 } from './fileUtils.js';

// Path to image to be edited
const sourceImagePath = "../images/man-in-orange.png";

const generateImages = async () => {
    // Format timestamp for unique directory naming
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const outputDirectory = `output/${timestamp}`;

    const generator = new BedrockImageGenerator({ outputDirectory });

    try {
        // Read the images from file and encode them as base64 strings
        const sourceImage = await imageToBase64(sourceImagePath);

        const params = {
            taskType: 'BACKGROUND_REMOVAL',
            backgroundRemovalParams: {
                image: sourceImage,
            },
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