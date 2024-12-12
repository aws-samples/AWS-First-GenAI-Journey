import { BedrockImageGenerator } from './BedrockImageGenerator.js';

const generateImages = async () => {
    // Format timestamp for unique directory naming
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const outputDirectory = `output/${timestamp}`;

    const generator = new BedrockImageGenerator({ outputDirectory });

    const params = {
        taskType: "TEXT_IMAGE",
        textToImageParams: {
            text: "whimsical and ethereal soft-shaded story illustration: A woman in a large hat stands at the ship's railing looking out across the ocean", // A description of the image you want
            negativeText: "clouds, waves" // List of things to avoid
        },
        imageGenerationConfig: {
            numberOfImages: 1,
            quality: "standard",  // Allowed values are "standard" and "premium"
            width: 1280,  // See README for supported output resolutions,
            height: 720,  // See README for supported output resolutions,
            cfgScale: 7.0,  // How closely the prompt will be followed,
            seed: Math.floor(Math.random() * 858993459), // Use a random seed     
        }
    };

    try {
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