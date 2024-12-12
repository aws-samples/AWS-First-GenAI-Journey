import { promises as fs } from 'fs';
import path from 'path';
import { BedrockRuntimeClient, GetAsyncInvokeCommand, ListAsyncInvokesCommand } from '@aws-sdk/client-bedrock-runtime';
import { S3Client, ListObjectsV2Command, GetObjectCommand } from '@aws-sdk/client-s3';
import winston from 'winston';
import Ffmpeg from 'fluent-ffmpeg';

// Configure logger
const logger = winston.createLogger({
    level: 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
    ),
    transports: [
        new winston.transports.Console()
    ]
});

// Initialize AWS clients
const bedrockRuntime = new BedrockRuntimeClient();
const s3Client = new S3Client();

/**
 * Saves invocation information and model input to the specified output folder
 * @param {Object} invocationResult - The result from the async invocation
 * @param {Object} modelInput - The input provided to the model
 * @param {string} [outputFolder='output'] - The base output folder path
 * @returns {Promise<string>} The absolute path to the created output folder
 */
async function saveInvocationInfo(invocationResult, modelInput, outputFolder = 'output') {
    const invocationArn = invocationResult.invocationArn;
    logger.info(`Getting async invoke details for ARN: ${invocationArn}`);

    const command = new GetAsyncInvokeCommand({ invocationArn });
    const invocationJob = await bedrockRuntime.send(command);
    const folderName = getFolderNameForJob(invocationJob);

    const outputFolderAbs = path.resolve(`${outputFolder}/${folderName}`);
    await fs.mkdir(outputFolderAbs, { recursive: true });
    logger.info(`Saving invocation info to folder: ${outputFolderAbs}`);

    await fs.writeFile(
        path.join(outputFolderAbs, 'start_async_invoke_response.json'),
        JSON.stringify(invocationResult, null, 2)
    );
    logger.info('Saved start_async_invoke_response.json');

    await fs.writeFile(
        path.join(outputFolderAbs, 'model_input.json'),
        JSON.stringify(modelInput, null, 2)
    );
    logger.info('Saved model_input.json');

    return outputFolderAbs;
}

/**
 * Generates a folder name based on the invocation job details
 * @param {Object} invocationJob - The invocation job object
 * @param {string} invocationJob.invocationArn - The ARN of the invocation
 * @param {string} invocationJob.submitTime - The submission timestamp
 * @returns {string} The generated folder name
 */
function getFolderNameForJob(invocationJob) {
    const invocationArn = invocationJob.invocationArn;
    const invocationId = invocationArn.split('/').pop();
    const submitTime = invocationJob.submitTime;
    const timestamp = new Date(submitTime).toLocaleString('sv').replace(/[\s:]/g, '-');
    const folderName = `${timestamp}_${invocationId}`;
    logger.info(`Generated folder name: ${folderName}`);
    return folderName;
}

/**
 * Checks if a video file already exists for a given invocation job
 * @param {Object} invocationJob - The invocation job object
 * @param {string} [outputFolder='output'] - The base output folder path
 * @returns {Promise<boolean>} True if the video exists, false otherwise
 */
async function isVideoDownloadedForInvocationJob(invocationJob, outputFolder = 'output') {
    const invocationArn = invocationJob.invocationArn;
    const invocationId = invocationArn.split('/').pop();
    const folderName = getFolderNameForJob(invocationJob);
    const outputFolderAbs = path.resolve(`${outputFolder}/${folderName}`);
    const fileName = `${invocationId}.mp4`;
    const videoPath = path.join(outputFolderAbs, fileName);

    try {
        await fs.access(videoPath);
        return true;
    } catch (error) {
        return false;
    }
}

/**
 * Downloads a video file from S3 for a given invocation ARN
 * @param {string} invocationArn - The ARN of the invocation
 * @param {string} bucketName - The S3 bucket name
 * @param {string} destinationFolder - The folder where the video will be saved
 * @returns {Promise<string>} The local path to the downloaded video file
 */
async function downloadVideoForInvocationArn(invocationArn, bucketName, destinationFolder) {
    const invocationId = invocationArn.split('/').pop();
    const fileName = `${invocationId}.mp4`;
    const outputFolderAbs = path.resolve(destinationFolder);
    await fs.mkdir(outputFolderAbs, { recursive: true });
    const localFilePath = path.join(outputFolderAbs, fileName);
    logger.info(`Downloading video file to: ${localFilePath}`);

    const command = new ListObjectsV2Command({
        Bucket: bucketName,
        Prefix: invocationId
    });

    const response = await s3Client.send(command);

    for (const obj of response.Contents || []) {
        const objectKey = obj.Key;
        if (objectKey.endsWith('.mp4')) {
            const getObjectCommand = new GetObjectCommand({
                Bucket: bucketName,
                Key: objectKey
            });
            const { Body } = await s3Client.send(getObjectCommand);

            // Convert the readable stream to a buffer
            const chunks = [];
            for await (const chunk of Body) {
                chunks.push(chunk);
            }
            const buffer = Buffer.concat(chunks);

            // Write the buffer to file
            await fs.writeFile(localFilePath, buffer);

            logger.info(`Downloaded video file: ${localFilePath}`);
            return localFilePath;
        }
    }

    logger.error(`Problem: No MP4 file was found in S3 at ${bucketName}/${invocationId}`);
}

/**
 * Calculates the elapsed time for an invocation job
 * @param {Object} invocationJob - The invocation job object
 * @param {string} invocationJob.submitTime - The job submission time
 * @param {string} [invocationJob.endTime] - The job end time (if completed)
 * @returns {number} The elapsed time in seconds
 */
function elapsedTimeForInvocationJob(invocationJob) {
    const invocationStartTime = new Date(invocationJob.submitTime).getTime() / 1000;
    let elapsedTime;

    if (invocationJob.endTime) {
        const invocationEndTime = new Date(invocationJob.endTime).getTime() / 1000;
        elapsedTime = Math.floor(invocationEndTime - invocationStartTime);
    } else {
        elapsedTime = Math.floor(Date.now() / 1000 - invocationStartTime);
    }

    return elapsedTime;
}

/**
 * Logs the progress of a job including elapsed time
 * @param {Object} job - The job object to log progress for
 */
function logJobProgress(job) {
    const jobId = getJobIdFromArn(job.invocationArn);
    const elapsedTime = elapsedTimeForInvocationJob(job);
    const minutes = Math.floor(elapsedTime / 60);
    const seconds = elapsedTime % 60;
    logger.info(
        `Job ${jobId} is still in progress, elapsed time: ${minutes} minutes ${seconds} seconds`
    );
}

/**
 * Monitors and downloads a video for a specific invocation ARN
 * @param {string} invocationArn - The ARN of the invocation
 * @param {string} [outputFolder='output'] - The output folder path
 * @returns {Promise<string>} The local path to the downloaded video file
 */
async function monitorAndDownloadVideo(invocationArn, outputFolder = 'output') {
    logger.info(`Monitoring and downloading video for ARN: ${invocationArn}`);
    const command = new GetAsyncInvokeCommand({ invocationArn });
    const invocationJob = await bedrockRuntime.send(command);
    const status = invocationJob.status;

    let localFilePath;
    if (status === 'Completed') {
        localFilePath = await saveCompletedJob(invocationJob, outputFolder);
    } else if (status === 'Failed') {
        await saveFailedJob(invocationJob, outputFolder);
    } else {
        localFilePath = await monitorAndDownloadInProgressVideo(invocationArn, outputFolder);
    }

    return localFilePath;
}

/**
 * Monitors and downloads an in-progress video
 * @param {string} invocationArn - The ARN of the invocation
 * @param {string} [outputFolder='output'] - The output folder path
 * @returns {Promise<string>} The local path to the downloaded video file
 */
async function monitorAndDownloadInProgressVideo(invocationArn, outputFolder = 'output') {
    logger.info(`Monitoring and downloading in-progress video for ARN: ${invocationArn}`);
    let jobUpdate = await bedrockRuntime.send(new GetAsyncInvokeCommand({ invocationArn }));
    let status = jobUpdate.status;

    while (status === 'InProgress') {
        logJobProgress(jobUpdate);
        await new Promise(resolve => setTimeout(resolve, 10000)); // Sleep for 10 seconds
        jobUpdate = await bedrockRuntime.send(new GetAsyncInvokeCommand({ invocationArn }));
        status = jobUpdate.status;
    }

    if (status === 'Completed') {
        const localFilePath = await saveCompletedJob(jobUpdate, outputFolder);
        return localFilePath;
    } else if (status === 'Failed') {
        await saveFailedJob(jobUpdate, outputFolder);
    } else {
        logger.error(`Unexpected status: ${status} for job ${invocationArn}`);
    }
}

/**
 * Monitors and downloads all videos based on job status
 * @param {string} [outputFolder='output'] - The output folder path
 * @param {string} [submitTimeAfter=null] - Optional timestamp to filter jobs
 */
async function monitorAndDownloadVideos(outputFolder = 'output', submitTimeAfter = null) {
    logger.info('Monitoring and downloading videos');

    // Handle failed jobs
    const failedJobsArgs = { statusEquals: 'Failed' };
    if (submitTimeAfter) {
        failedJobsArgs.submitTimeAfter = submitTimeAfter;
    }

    const failedJobsCommand = new ListAsyncInvokesCommand(failedJobsArgs);
    const failedJobs = await bedrockRuntime.send(failedJobsCommand);
    for (const job of failedJobs.asyncInvokeSummaries) {
        await saveFailedJob(job, outputFolder);
    }

    // Handle completed jobs
    const completedJobsArgs = { statusEquals: 'Completed' };
    if (submitTimeAfter) {
        completedJobsArgs.submitTimeAfter = submitTimeAfter;
    }

    const completedJobsCommand = new ListAsyncInvokesCommand(completedJobsArgs);
    const completedJobs = await bedrockRuntime.send(completedJobsCommand);
    for (const job of completedJobs.asyncInvokeSummaries) {
        await saveCompletedJob(job, outputFolder);
    }

    await monitorAndDownloadInProgressVideos(outputFolder);
}

/**
 * Monitors and downloads videos for in-progress jobs
 * @param {string} [outputFolder='output'] - The output folder path
 */
async function monitorAndDownloadInProgressVideos(outputFolder = 'output') {
    logger.info('Monitoring and downloading in-progress videos');
    const listCommand = new ListAsyncInvokesCommand({ statusEquals: 'InProgress' });
    const invocationList = await bedrockRuntime.send(listCommand);
    const inProgressJobs = invocationList.asyncInvokeSummaries;
    let pendingJobArns = inProgressJobs.map(job => job.invocationArn);

    while (pendingJobArns.length > 0) {
        const jobArnsToRemove = [];

        for (const jobArn of pendingJobArns) {
            const command = new GetAsyncInvokeCommand({ invocationArn: jobArn });
            const jobUpdate = await bedrockRuntime.send(command);
            const status = jobUpdate.status;

            if (status === 'Completed' || status === 'Failed') {
                if (status === 'Completed') {
                    await saveCompletedJob(jobUpdate, outputFolder);
                } else {
                    await saveFailedJob(jobUpdate, outputFolder);
                }
                jobArnsToRemove.push(jobArn);
            } else {
                logJobProgress(jobUpdate);
            }
        }

        pendingJobArns = pendingJobArns.filter(arn => !jobArnsToRemove.includes(arn));
        await new Promise(resolve => setTimeout(resolve, 10000)); // Sleep for 10 seconds
    }

    logger.info('Monitoring and download complete!');
}

/**
 * Extracts the job ID from an invocation ARN
 * @param {string} invocationArn - The ARN of the invocation
 * @returns {string} The extracted job ID
 */
function getJobIdFromArn(invocationArn) {
    return invocationArn.split('/').pop();
}

/**
 * Saves details for a completed job and downloads its video
 * @param {Object} job - The completed job object
 * @param {string} [outputFolder='output'] - The output folder path
 * @returns {Promise<string>} The local path to the downloaded video file
 */
async function saveCompletedJob(job, outputFolder = 'output') {
    const jobId = getJobIdFromArn(job.invocationArn);
    const outputFolderAbs = path.resolve(`${outputFolder}/${getFolderNameForJob(job)}`);
    await fs.mkdir(outputFolderAbs, { recursive: true });
    logger.info(`Saving completed job details for job ${jobId}`);

    const statusFile = path.join(outputFolderAbs, 'completed.json');

    const videoExists = await isVideoDownloadedForInvocationJob(job, outputFolder);
    if (videoExists) {
        logger.info(`Skipping completed job ${jobId}, video already downloaded.`);
        return;
    }

    const s3BucketName = job.outputDataConfig.s3OutputDataConfig.s3Uri
        .split('//')[1]
        .split('/')[0];

    const localFilePath = await downloadVideoForInvocationArn(
        job.invocationArn,
        s3BucketName,
        outputFolderAbs
    );

    await fs.writeFile(statusFile, JSON.stringify(job, null, 2));
    logger.info(`Saved completed job details to ${statusFile}`);

    return localFilePath;
}

/**
 * Saves details for a failed job
 * @param {Object} job - The failed job object
 * @param {string} [outputFolder='output'] - The output folder path
 */
async function saveFailedJob(job, outputFolder = 'output') {
    const outputFolderAbs = path.resolve(`${outputFolder}/${getFolderNameForJob(job)}`);
    const outputFile = path.join(outputFolderAbs, 'failed.json');

    const jobId = getJobIdFromArn(job.invocationArn);

    try {
        await fs.access(outputFile);
        logger.info(`Skipping failed job ${jobId}, output file already exists.`);
        return;
    } catch (error) {
        await fs.mkdir(outputFolderAbs, { recursive: true });
        await fs.writeFile(outputFile, JSON.stringify(job, null, 2));
        logger.info(`Saved failed job details to ${outputFile}`);
    }
}

/**
 * Converts an image file to base64 string
 * @param {string} inputImagePath - The path to the input image file
 * @returns {Promise<string>} The base64 encoded string of the image
 * @throws {Error} If the image conversion fails
 */
async function imageToBase64(inputImagePath) {
    try {
        // Read the file
        const inputImageBytes = await fs.readFile(inputImagePath);

        // Convert to base64
        const inputImageBase64 = inputImageBytes.toString('base64');

        return inputImageBase64;
    } catch (error) {
        console.error('Error converting image to base64:', error);
        throw error;
    }
}

/**
 * Extracts the last frame of a video file.
 * 
 * @param {string} videoPath - The local path to the video to extract the last frame from.
 * @param {string} outputPath - The local path to save the extracted frame to.
 * @returns {Promise<void>}
 */
function extractLastFrame(videoPath, outputPath) {
    return new Promise((resolve, reject) => {
        // First, get the duration of the video
        Ffmpeg.ffprobe(videoPath, (err, metadata) => {
            if (err) {
                logger.error("Error: Could not open video.", err);
                return reject(err);
            }

            const duration = metadata.format.duration;

            // Extract the last frame by seeking to the end of the video
            Ffmpeg(videoPath)
                .seekInput(duration - 0.05) // Seek to just before the end
                .frames(1) // Extract only one frame
                .output(outputPath)
                .on('end', () => {
                    logger.info(`Last frame saved as ${outputPath}`);
                    resolve();
                })
                .on('error', (err) => {
                    logger.error("Error: Could not extract the last frame.", err);
                    reject(err);
                })
                .run();
        });
    });
}

/**
 * Concatenates two video files into a single output video
 * @param {string} video1Path - Path to the first video file
 * @param {string} video2Path - Path to the second video file
 * @param {string} outputPath - Path where the concatenated video should be saved
 * @returns {Promise} Resolves when concatenation is complete
 */
async function stitchVideos(video1Path, video2Path, outputPath) {
    try {
        // Check if input files exist using fs.access
        await Promise.all([
            fs.access(video1Path),
            fs.access(video2Path)
        ]);

        // Return a promise that resolves when the merge is complete
        return new Promise((resolve, reject) => {
            Ffmpeg(video1Path)
                .input(video2Path)
                .mergeToFile(outputPath)
                .on('end', () => {
                    logger.info('Files have been merged successfully');
                    resolve();
                })
                .on('error', (err) => {
                    logger.error('An error happened: ' + err.message);
                    reject(err);
                });
        });
    } catch (error) {
        throw error;
    }
}



export {
    saveInvocationInfo,
    getFolderNameForJob,
    isVideoDownloadedForInvocationJob,
    downloadVideoForInvocationArn,
    elapsedTimeForInvocationJob,
    monitorAndDownloadVideo,
    monitorAndDownloadVideos,
    monitorAndDownloadInProgressVideos,
    saveCompletedJob,
    saveFailedJob,
    getJobIdFromArn,
    imageToBase64,
    extractLastFrame,
    stitchVideos
};