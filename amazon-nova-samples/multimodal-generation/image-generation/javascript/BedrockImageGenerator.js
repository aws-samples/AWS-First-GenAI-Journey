import { promises as fs } from 'fs';
import { join } from 'path';
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';
import winston from 'winston';

// Configure logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [new winston.transports.Console()]
});


/**
 * Custom error class for image generation related errors
 * @extends Error
 */
class ImageGenerationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ImageGenerationError';
    }
}

/**
 * Class for generating images using Amazon Bedrock
 */
class BedrockImageGenerator {
    static DEFAULT_MODEL_ID = 'amazon.nova-canvas-v1:0';
    static DEFAULT_REGION = 'us-east-1';

    /**
     * Creates an instance of BedrockImageGenerator
     * @param {Object} options - Configuration options
     * @param {string} [options.regionName=DEFAULT_REGION] - AWS region name
     * @param {string} [options.outputDirectory='./output'] - Directory to save generated files
     */
    constructor({
        regionName = BedrockImageGenerator.DEFAULT_REGION,
        outputDirectory = './output'
    } = {}) {
        this.regionName = regionName;
        this.outputDirectory = outputDirectory;
        this.bedrockClient = new BedrockRuntimeClient({ region: this.regionName });
    }

    /**
     * Saves data to a file
     * @param {Buffer | object} data - Data to save
     * @param {string} filename - Name of the file
     * @param {boolean} [isBinary=false] - Whether the data is binary
     * @throws {ImageGenerationError} If file saving fails
     */
    async saveFile(data, filename, isBinary = false) {
        try {
            const filepath = join(this.outputDirectory, filename);
            const content = isBinary ? data : JSON.stringify(data, null, 2);
            await fs.writeFile(filepath, content);
        } catch (error) {
            logger.error(`Failed to save ${filename}: ${error.message}`);
            throw new ImageGenerationError(`Failed to save ${filename}`);
        }
    }

    /**
     * Generates images using Amazon Bedrock
     * @param {Object} inferenceParams - Parameters for image generation
     * @param {string} [modelId=DEFAULT_MODEL_ID] - Model ID to use for generation
     * @returns {Promise<string[]>} Array of paths to generated images
     * @throws {ImageGenerationError} If image generation fails
     */
    async generateImages(inferenceParams, modelId = BedrockImageGenerator.DEFAULT_MODEL_ID) {
        try {
            await fs.mkdir(this.outputDirectory, { recursive: true });

            const imageCount = inferenceParams?.imageGenerationConfig?.numberOfImages ?? 1;
            logger.info(`Generating ${imageCount} image(s) with ${modelId} in region ${this.regionName}`);

            if (inferenceParams?.imageGenerationConfig?.seed !== undefined) {
                logger.info(`Using seed: ${inferenceParams.imageGenerationConfig.seed}`);
            }

            // Save request
            await this.saveFile(inferenceParams, 'request.json');

            // Make API call
            const command = new InvokeModelCommand({
                body: JSON.stringify(inferenceParams),
                modelId,
                accept: 'application/json',
                contentType: 'application/json'
            });

            const response = await this.bedrockClient.send(command);
            const imagePaths = []

            // Save response metadata
            await this.saveFile(response.ResponseMetadata || {}, 'response_metadata.json');

            // Process response
            if (!(response.body instanceof Uint8Array)) {
                throw new Error('Unexpected response format: Expected Uint8Array');
            }

            const responseBody = JSON.parse(Buffer.from(response.body).toString('utf-8'));
            await this.saveFile(responseBody, 'response_body.json');

            // Save generated images
            if (responseBody.images?.length) {
                await Promise.all(responseBody.images.map((imageBase64, index) => {
                    const imageBuffer = Buffer.from(imageBase64, 'base64');
                    imagePaths.push(`${this.outputDirectory}/image_${index + 1}.png`);
                    return this.saveFile(imageBuffer, `image_${index + 1}.png`, true);
                }));
            }

            // Log request ID and check for errors
            if (response.ResponseMetadata?.RequestId) {
                logger.info(`Request ID: ${response.ResponseMetadata.RequestId}`);
            }

            if (responseBody.error) {
                logger.warn(`Error in response: ${responseBody.error}`);
            }

            return imagePaths;

        } catch (error) {
            const errorMessage = error.name === 'ServiceError' 
                ? 'Failed to generate images: AWS service error'
                : 'Unexpected error during image generation';

            logger.error(`${errorMessage}: ${error.message}`);
            
            if (error.response) {
                await this.saveFile(error.response, 'error_response.json');
            }

            throw new ImageGenerationError(errorMessage);
        }
    }
}

export { BedrockImageGenerator, ImageGenerationError };