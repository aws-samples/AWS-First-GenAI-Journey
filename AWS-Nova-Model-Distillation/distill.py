"""Amazon Nova Model Distillation - create smaller, faster models from larger ones."""

import os
import boto3
import time

bedrock = boto3.client("bedrock", region_name=os.environ.get("AWS_REGION", "us-east-1"))


def start_distillation_job(
    job_name: str,
    teacher_model_id: str,
    student_model_id: str,
    training_data_s3: str,
    output_s3: str,
    max_epochs: int = 3,
    batch_size: int = 8,
    learning_rate: float = 1e-5,
):
    """Launch a model distillation job using Bedrock create_model_customization_job."""
    response = bedrock.create_model_customization_job(
        jobName=job_name,
        customModelName=f"{job_name}-distilled",
        roleArn="arn:aws:iam::ACCOUNT_ID:role/BedrockDistillationRole",
        baseModelIdentifier=student_model_id,
        customizationType="DISTILLATION",
        trainingDataConfig={"s3Uri": training_data_s3},
        outputDataConfig={"s3Uri": output_s3},
        hyperParameters={
            "epochCount": str(max_epochs),
            "batchSize": str(batch_size),
            "learningRate": str(learning_rate),
        },
        teacherModelConfig={"teacherModelIdentifier": teacher_model_id, "maxResponseLengthForInference": 2048},
    )
    return response["jobArn"]


def get_job_status(job_arn: str) -> dict:
    """Check the status of a distillation job."""
    return bedrock.get_model_customization_job(jobIdentifier=job_arn)


def wait_for_completion(job_arn: str, poll_interval: int = 60) -> dict:
    """Poll until the distillation job completes."""
    while True:
        status = get_job_status(job_arn)
        if status["status"] in ("Completed", "Failed", "Stopped"):
            return status
        time.sleep(poll_interval)
