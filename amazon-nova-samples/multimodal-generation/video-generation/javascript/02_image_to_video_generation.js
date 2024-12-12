#!/usr/bin/env node

import {
    BedrockRuntimeClient,
    StartAsyncInvokeCommand,
} from '@aws-sdk/client-bedrock-runtime';
import { S3Client, CreateBucketCommand } from '@aws-sdk/client-s3';
import winston from 'winston';
import { monitorAndDownloadVideo, saveInvocationInfo, imageToBase64 } from './amazonVideoUtil.js';

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
 * Generates a video from an image using the specified prompt and model.
 * @param {string} s3DestinationBucket - The S3 bucket to store the generated video.
 * @param {string} videoPrompt - The prompt for video generation.
 * @param {string} inputImageBase64 - The base64 encoded image to use as input.
 * @param {string} [modelId=DEFAULT_MODEL_ID] - The model ID to use for video generation.
 * @returns {Promise<string|null>} - The ARN of the invocation if successful, otherwise null.
 */
async function generateVideoFromImage(s3DestinationBucket, videoPrompt, inputImageBase64, modelId = DEFAULT_MODEL_ID) {
    try {
        // Create the S3 bucket
        await s3Client.send(new CreateBucketCommand({
            Bucket: s3DestinationBucket
        }));

        const modelInput = {
            taskType: "TEXT_VIDEO",
            textToVideoParams: {
                text: videoPrompt,
                images: [
                    {
                        format: "png",
                        source: {
                            bytes: inputImageBase64
                        }
                    }
                ]
            },
            videoGenerationConfig: {
                durationSeconds: 6,
                fps: 24,
                dimension: "1280x720",
                seed: Math.floor(Math.random() * 2147483648),
            },
        };

        console.log(modelInput)

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
    const VIDEO_PROMPT = "Closeup of a large seashell in the sand, gentle waves flow around the shell. Camera zoom in.";
    const MODEL_ID = "amazon.nova-reel-v1:0";

    const inputImageBase64 = await imageToBase64('../images/sample-frame-1.png')

    // Generate video
    const invocationArn = await generateVideoFromImage(S3_BUCKET, VIDEO_PROMPT, inputImageBase64, MODEL_ID);
    if (!invocationArn) {
        logger.error("Failed to start video generation");
        process.exit(1);
    }

    // Monitor and download the video
    logger.info("\nMonitoring job and waiting for completion...");
    const localFilePath = await monitorAndDownloadVideo(invocationArn, "output");

    if (localFilePath) {
        logger.info(`\nVideo successfully generated and downloaded to: ${localFilePath}`);
    } else {
        logger.info("\nFailed to generate or download video");
    }
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