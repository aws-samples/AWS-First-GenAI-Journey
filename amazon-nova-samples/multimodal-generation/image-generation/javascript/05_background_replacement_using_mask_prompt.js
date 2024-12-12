import { BedrockImageGenerator } from './BedrockImageGenerator.js';
import { imageToBase64 } from './fileUtils.js';

const sourceImagePath = "../images/amazon-coffee-maker-1.png";

const generateImages = async () => {
    // Format timestamp for unique directory naming
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const outputDirectory = `output/${timestamp}`;

    const generator = new BedrockImageGenerator({ outputDirectory });

    try {
        // Read the image from file and encode it as base64 string
        const sourceImage = await imageToBase64(sourceImagePath);

        const params = {
            taskType: 'OUTPAINTING',
            outPaintingParams: {
                image: sourceImage,
                text: "a coffee maker in a sparse stylish kitchen, a single plate of pastries next to the coffee maker, a single cup of coffee. highly detailed, highest quality, product imagery",  // Description of the background to generate
                maskPrompt: "coffee maker",  // The element(s) to keep
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