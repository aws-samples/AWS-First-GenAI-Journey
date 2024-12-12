# Amazon Nova Reel Video Generator Code Samples

This repository includes code examples for common image generation and editing tasks using AmazonNova Reel video generation model. Examples are provided in Python (.py), Jupyter Notebook (.ipynb), and Javascript (.js) formats. Sample images for use with these scripts have also been provided.

## Setup - Permissions and Model Entitlement

### Prerequisites

- Your AWS account has been allow-listed for access to the model.
- You have the AWS CLI installed.
- You have used the AWS CLI to set the "default" AWS credentials to those associated with your allow-listed account.
- You have Python installed.
- You have a way to run Jupyter Notebooks.
- The `03` example requires having [ffmpeg](https://www.ffmpeg.org/) installed on your machine.

### One-time setup

The following steps only need to be performed once during your initial setup.

#### Add necessary AWS permissions to your user profile

Using Nova Reel requires that you have permissions allowing access to the following AWS Actions:

- "s3:PutObject"
- "bedrock:\*"

Because the code in these notebooks and scripts provide some additional conveniences - like creating an S3 bucket and automatically downloading generated video files - you'll need a few additional permissions in order to use them. The required permissions are listed below. If the IAM user you plan to use already has these permissions, there is no need to take any action. Otherwise, attach the following premissions policy to that user in the AWS console. (This guide assumes you know how to apply permissions policies through the console.)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "NovaReelUserPermissions",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:CreateBucket",
                "s3:ListBucket",
                "bedrock:*"
            ],
            "Resource": "*"
        }
    ]
}
```

After applying the policy, it may take a couple minutes for the policy to take effect. If you receive a permissions error when running the notebooks/scripts, wait a couple minutes and try again.

#### Enable the model on Amazon Bedrock

You will then need to run the following command to enable access to the Nova Reel model in your account.

```bash
python entitlement.py us-east-1 amazon.nova-reel-v1:0
```

## Setup - Python

If you are running the Python scripts outside of a Jupyter Notebook, you'll need to first install the required dependencies by running the following command from the `python` directory:

```bash
pip install -r requirements.txt
```

You will then be able to run the scripts as follows:

```bash
python 01_simple_video_generation.py
```

## Setup - Javascript

To run the Javascript scripts, you'll first need to install the required packages by running the following command from the `javascript` directory:

```bash
npm install
```

You will then be able to run the scripts as follows:

```bash
node 01_simple_video_generation.js
```