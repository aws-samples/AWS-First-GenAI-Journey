import { BedrockImageGenerator } from './BedrockImageGenerator.js';

const generateImages = async () => {
    // Format timestamp for unique directory naming
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const outputDirectory = `output/${timestamp}`;

    const generator = new BedrockImageGenerator({ outputDirectory });

    const params = {
        taskType: 'COLOR_GUIDED_GENERATION',
        colorGuidedGenerationParams: {
            text: 'digital painting of a girl, dreamy and ethereal',
            colors: ['#81FC81', '#386739', '#C9D688', '#FFFFFF', '#FFFFFF'],
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