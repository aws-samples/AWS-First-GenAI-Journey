#!/usr/bin/env node

import { promises as fs } from 'fs';
import path from 'path';
import {
    BedrockRuntimeClient,
    StartAsyncInvokeCommand,
} from '@aws-sdk/client-bedrock-runtime';
import { S3Client, CreateBucketCommand } from '@aws-sdk/client-s3';
import winston from 'winston';
import { monitorAndDownloadVideo, saveInvocationInfo, extractLastFrame, imageToBase64, stitchVideos } from './amazonVideoUtil.js';

// Configure logging
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.simple(),
    transports: [
        new winston.transports.Console()
    ]
});

// Constants
const DEFAULT_MODEL_ID = "amazon.nova-reel-v1:0";

// Initialize AWS clients
let bedrockRuntime;
let s3Client;

/**
 * Initializes AWS Bedrock Runtime and S3 clients.
 * @param {string} [region="us-east-1"] - The AWS region to initialize clients for.
 */
function setupAwsSession(region = "us-east-1") {
    bedrockRuntime = new BedrockRuntimeClient({ region });
    s3Client = new S3Client({ region });
    logger.info("AWS SDK clients have been initialized.");
}

/**
 * Generates a video using the specified prompt and model. Optionally uses an input image.
 * @param {string} s3DestinationBucket - The S3 bucket to store the generated video.
 * @param {string} videoPrompt - The prompt for video generation.
 * @param {string} [inputImageBase64] - The base64 encoded image to use as input (optional).
 * @param {string} [modelId=DEFAULT_MODEL_ID] - The model ID to use for video generation.
 * @returns {Promise<string|null>} - The ARN of the invocation if successful, otherwise null.
 */
async function generateVideo(s3DestinationBucket, videoPrompt, inputImageBase64 = null, modelId = DEFAULT_MODEL_ID) {
    try {
        // Create the S3 bucket
        await s3Client.send(new CreateBucketCommand({
            Bucket: s3DestinationBucket
        }));

        const modelInput = {
            taskType: "TEXT_VIDEO",
            textToVideoParams: {
                text: videoPrompt,
            },
            videoGenerationConfig: {
                durationSeconds: 6,
                fps: 24,
                dimension: "1280x720",
                seed: Math.floor(Math.random() * 2147483648),
            },
        };

        if (inputImageBase64) {
            modelInput.textToVideoParams.images = [
                {
                    format: "png",
                    source: {
                        bytes: inputImageBase64
                    }
                }
            ];
        }

        const command = new StartAsyncInvokeCommand({
            modelId: modelId,
            contentType: "application/json",
            accept: "application/json",
            modelInput: modelInput,
            outputDataConfig: {
                s3OutputDataConfig: {
                    s3Uri: `s3://${s3DestinationBucket}`
                }
            }
        });

        const invocation = await bedrockRuntime.send(command);
        const invocationArn = invocation.invocationArn;

        logger.info("\nResponse:");
        logger.info(JSON.stringify(invocation, null, 2));

        await saveInvocationInfo(invocation, modelInput);

        return invocationArn;

    } catch (error) {
        logger.error(error);
        return null;
    }
}

/**
 * The main function to orchestrate video generation, status checking, and downloading.
 * @returns {Promise<void>} - A promise that resolves when the main function completes.
 */
async function main() {
    // Initialize the AWS session
    setupAwsSession();

    // Configuration
    const S3_BUCKET = "nova-videos"; // Change this to your unique bucket name
    const VIDEO_PROMPT_1 = "First person view walking through light snowfall in a forest, sunlight through trees, dolly forward, cinematic"
    const VIDEO_PROMPT_2 = "First person view entering a clearing with heavy snowfall, sun creating diamond-like sparkles, continuing dolly forward, cinematic"
    const MODEL_ID = "amazon.nova-reel-v1:0";

    // Generate the first video
    const invocationArn1 = await generateVideo(S3_BUCKET, VIDEO_PROMPT_1, null, MODEL_ID);
    if (!invocationArn1) {
        logger.error("Failed to start video generation");
        process.exit(1);
    }

    // Monitor and download the video
    logger.info("\nMonitoring job and waiting for completion...");
    const localFilePath1 = await monitorAndDownloadVideo(invocationArn1, "output");

    if (localFilePath1) {
        logger.info(`\nVideo successfully generated and downloaded to: ${localFilePath1}`);
    } else {
        logger.info("\nFailed to generate or download video");
    }

    // Define and create an output directory with a unique name.
    const generationId = new Date().toISOString().replace(/[-:.TZ]/g, '');
    const outputDirectory = path.join('output', generationId);
    await fs.mkdir(outputDirectory, { recursive: true });

    // Extract the last frame from the video
    const lastFramePath = `${outputDirectory}/last_frame.png`
    await extractLastFrame(localFilePath1, lastFramePath)
    const inputImageBase64 = await imageToBase64(lastFramePath)

    // Generate the second video
    const invocationArn2 = await generateVideo(S3_BUCKET, VIDEO_PROMPT_2, inputImageBase64, MODEL_ID);
    if (!invocationArn2) {
        logger.error("Failed to start video generation");
        process.exit(1);
    }

    // Monitor and download the video
    logger.info("\nMonitoring job and waiting for completion...");
    const localFilePath2 = await monitorAndDownloadVideo(invocationArn2, "output");

    if (localFilePath2) {
        logger.info(`\nVideo successfully generated and downloaded to: ${localFilePath2}`);
    } else {
        logger.info("\nFailed to generate or download video");
    }

    // Create output path for merged video
    const outputPath = `${outputDirectory}/merged_video.mp4`;

    // Stitch the two video generations together
    await stitchVideos(localFilePath1, localFilePath2, outputPath);
}

// Self-executing async function
(async () => {
    try {
        await main();
    } catch (err) {
        console.error('Fatal error:', err.message);
        process.exit(1);
    }
})();