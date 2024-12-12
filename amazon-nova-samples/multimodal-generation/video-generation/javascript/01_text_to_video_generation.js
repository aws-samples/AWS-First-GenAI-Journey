#!/usr/bin/env node

import { 
    BedrockRuntimeClient, 
    StartAsyncInvokeCommand, 
    GetAsyncInvokeCommand, 
    ListAsyncInvokesCommand 
} from '@aws-sdk/client-bedrock-runtime';
import { S3Client, CreateBucketCommand } from '@aws-sdk/client-s3';
import winston from 'winston';
import {monitorAndDownloadVideo, monitorAndDownloadVideos, saveInvocationInfo} from './amazonVideoUtil.js';

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
 * Generates a video using the specified prompt and model.
 * @param {string} s3DestinationBucket - The S3 bucket to store the generated video.
 * @param {string} videoPrompt - The prompt for video generation.
 * @param {string} [modelId=DEFAULT_MODEL_ID] - The model ID to use for video generation.
 * @returns {Promise<string|null>} - The ARN of the invocation if successful, otherwise null.
 */
async function generateVideo(s3DestinationBucket, videoPrompt, modelId = DEFAULT_MODEL_ID) {
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
 * Checks the status of a video generation job.
 * @param {string} invocationArn - The ARN of the invocation.
 * @returns {Promise<Object|null>} - The response from the GetAsyncInvokeCommand if successful, otherwise null.
 */
async function checkJobStatus(invocationArn) {
    try {
        const command = new GetAsyncInvokeCommand({ invocationArn });
        const response = await bedrockRuntime.send(command);
        
        const status = response.status;
        logger.info(`Status: ${status}`);
        logger.info("\nFull response:");
        logger.info(JSON.stringify(response, null, 2));
        return response;
    } catch (error) {
        logger.error(`Error checking job status: ${error}`);
        return null;
    }
}

/**
 * Lists the statuses of video generation jobs.
 * @param {number} [maxResults=10] - The maximum number of results to return.
 * @param {string} [statusFilter="InProgress"] - The status filter for the jobs.
 * @returns {Promise<Object|null>} - The response from the ListAsyncInvokesCommand if successful, otherwise null.
 */
async function listJobStatuses(maxResults = 10, statusFilter = "InProgress") {
    try {
        const command = new ListAsyncInvokesCommand({
            maxResults: maxResults,
            statusEquals: statusFilter,
        });
        
        const invocation = await bedrockRuntime.send(command);
        
        logger.info("Invocation Jobs:");
        logger.info(JSON.stringify(invocation, null, 2));
        return invocation;
    } catch (error) {
        logger.error(`Error listing jobs: ${error}`);
        return null;
    }
}

/**
 * Monitors recent video generation jobs and downloads the videos.
 * @param {number} [durationHours=1] - The duration in hours to monitor jobs for.
 * @returns {Promise<void>} - A promise that resolves when the monitoring is complete.
 */
async function monitorRecentJobs(durationHours = 1) {
    const fromSubmitTime = new Date(Date.now() - durationHours * 60 * 60 * 1000);
    return await monitorAndDownloadVideos("output", fromSubmitTime);
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

    // Generate video
    const invocationArn = await generateVideo(S3_BUCKET, VIDEO_PROMPT, MODEL_ID);
    if (!invocationArn) {
        logger.error("Failed to start video generation");
        process.exit(1);
    }

    // Check initial status
    logger.info("\nChecking initial job status...");
    await checkJobStatus(invocationArn);

    // List all in-progress jobs
    logger.info("\nListing all in-progress jobs...");
    await listJobStatuses();

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