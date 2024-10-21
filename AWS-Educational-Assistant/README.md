### AWS Educational Assistant: Technical Overview

The **AWS Educational Assistant** project demonstrates the integration of Amazon Bedrock and Anthropic's Claude 3 Sonnet model. It illustrates how these services, combined with Langchain and a Streamlit web interface, can be used to build an educational assistant application. This guide provides a step-by-step approach to deploying and running the project.

---

### Key Features

1. **Amazon Bedrock Integration**:
   - Leverages Amazon Bedrock to access powerful foundation models, such as Claude 3, in a scalable, serverless manner.

2. **Anthropic Claude 3 Sonnet**:
   - Utilizes Claude 3 Sonnet for advanced natural language understanding and generation, enabling meaningful educational interactions.

3. **Langchain Integration**:
   - Incorporates Langchain for chaining complex workflows and prompts, allowing efficient task automation and language model-driven responses.

4. **Streamlit Web Interface**:
   - Provides a real-time, interactive user interface for users to engage with the assistant via Streamlit.

---

### Prerequisites

1. **Python (version 3.8 or later)**
2. **AWS CLI** (configured for Amazon Bedrock usage)
3. **Git** (to clone the project repository)

---

### Step-by-Step Setup Guide

#### 1. Install Python

First, ensure Python is installed on your system. You can follow this installation guide based on your operating system:

- [Python Installation Guide](https://docs.python-guide.org/starting/install3/linux/)

To verify the installation, run:

```bash
python3 --version
```

#### 2. Set Up a Python Virtual Environment

To avoid dependency conflicts, create a Python virtual environment for this project:

```bash
python3 -m venv educational_assistant_env
source educational_assistant_env/bin/activate  # For Linux/Mac
# or
.\educational_assistant_env\Scripts\activate   # For Windows
```

#### 3. Install and Configure AWS CLI

You’ll need AWS CLI to authenticate and interact with Amazon Bedrock. Install AWS CLI following this guide:

- [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

After installation, configure it using:

```bash
aws configure
```

Make sure you set the AWS region to one that supports Bedrock, such as `us-west-2`.

#### 4. Clone the AWS Educational Assistant Repository

Now, clone the project from GitHub:

```bash
git clone https://github.com/
cd AWS-Educational-Assistant
```

#### 5. Install Project Dependencies

Install all required Python packages by using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

This installs necessary libraries like `streamlit`, `boto3`, `langchain`, and others.

#### 6. Run the Streamlit Application

To start the application, run:

```bash
streamlit run Home.py --server.port 8080
```

The application will run on port `8080`. You can access it via your browser at `http://localhost:8080`.

---

### Additional Resources

- **Amazon Bedrock Documentation**:
  - [Amazon Bedrock](https://aws.amazon.com/bedrock/)

- **Prompt Engineering Guide**:
  - [Introduction to Prompt Design](https://docs.anthropic.com/claude/docs/introduction-to-prompt-design)

- **Claude 3 Model Card**:
  - [Claude 3 Model Card](https://www-cdn.anthropic.com/de8ba9b01c9ab7cbabf5c33b80b7bbc618857627/Model_Card_Claude_3.pdf)

This guide serves as a foundation to get the **AWS Educational Assistant** up and running, demonstrating the powerful combination of Amazon Bedrock, Claude 3, Langchain, and Streamlit.