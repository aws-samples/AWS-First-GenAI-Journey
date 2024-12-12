# Amazon Nova Canvas Image Generator Code Samples

This repository includes code examples for common image generation and editing tasks using AmazonNova Canvas image generation model. Examples are provided in Python (.py), Jupyter Notebook (.ipynb), and Javascript (.js) formats. Sample images for use with these scripts have also been provided.

## Setup - Permissions and Model Entitlement

### Prerequisites

- Your AWS account has been allow-listed for access to the model.
- You have installed the AWS CLI.
- You have configured the AWS CLI **default profile** to use the credentials for your allow-listed account
- You have Python installed.

### One-time setup

The following steps only need to be performed once during your initial setup.

#### Add necessary AWS permissions to your user profile

Using Nova Canvas requires that you have permissions allowing access to the following AWS Actions:

- "bedrock:InvokeModel"

The required permissions are listed below. If the user you've set as your AWS CLI default already has these permissions, there is no need to take any action. Otherwise, attach the following premissions policy to that user in the AWS console. (This guide assumes you know how to appy permissions policies through the console.)

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "NovaCanvasUserPermissions",
            "Effect": "Allow",
            "Action": ["bedrock:InvokeModel", "bedrock:PutFoundationModelEntitlement"],
            "Resource": ["arn:aws:bedrock:*::foundation-model/*"]
        }
    ]
}
```

After applying the policy, it may take a couple minutes for the policy to take effect. If you receive a permissions error when running the notebooks/scripts, wait a couple minutes and try again.

#### Enable the model on Amazon Bedrock

Run the following cell to enable access to the Nova Canvas model in your account.

```bash
python entitlement.py us-east-1 amazon.nova-reel-v1:0
```

## Setup - Python

If you are running the Python scripts outside of a Jupyter Notebook, you'll need to first install the required dependencies by running the following command from the `python` directory:

```bash
python3 -m pip install -r requirements.txt
```

You will then be able to run the scripts as follows:

```bash
python3 01_simple_image_generation.py
```

## Setup - Javascript

To run the Javascript scripts, you'll first need to install the required packages by running the following command from the `javascript` directory:

```bash
npm install
```

You will then be able to run the scripts as follows:

```bash
node 01_simple_image_generation.js
```