### AWS Educational Assistant: Technical Overview

The **AWS Educational Assistant** is a demonstration project that integrates Amazon Bedrock and Anthropic's Claude 3 Sonnet model. It highlights how these services can be combined with Langchain and a Streamlit interface to build an educational assistant application. This project serves as a foundation for those looking to create similar language model-driven applications.

### Key Features

1. **Amazon Bedrock Integration**:
   - Uses Amazon Bedrock to access foundation models, providing scalable, serverless integration with models like Claude 3.
   
2. **Anthropic Claude 3 Sonnet**:
   - Leverages Claude 3, known for its natural language understanding and generation, allowing for meaningful interactions and answers based on educational content.
   
3. **Langchain Integration**:
   - Langchain is employed for creating complex workflows involving language models, allowing for chaining multiple prompts and tasks efficiently.
   
4. **Streamlit Web Interface**:
   - A lightweight, interactive web app using Streamlit that provides a front-end for users to interact with the assistant in real-time.

---

### Prerequisites

1. **Python (version 3.8 or later)**
2. **AWS CLI** (configured with appropriate access credentials to use Amazon Bedrock)
3. **Git** (for cloning the repository)

---

### Step-by-Step Setup Guide

#### 1. Install Python

To get started, ensure that you have Python installed on your system. You can follow the installation guide specific to your operating system:

- [Python Installation Guide](https://docs.python-guide.org/starting/install3/linux/)

Verify the installation by running:

```bash
python3 --version
```

#### 2. Set Up Python Virtual Environment

It's recommended to create a virtual environment to manage dependencies. Use the following commands to create and activate one:

```bash
python3 -m venv educational_assistant_env
source educational_assistant_env/bin/activate  # Linux/Mac
# or
.\educational_assistant_env\Scripts\activate   # Windows
```

#### 3. Install AWS CLI

Amazon Bedrock requires AWS CLI configuration. To install and configure AWS CLI, follow the instructions here:

- [AWS CLI Quickstart Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)

After installation, configure AWS CLI with:

```bash
aws configure
```

Ensure that the AWS region is set to one that supports Bedrock (e.g., `us-west-2`).

#### 4. Clone the AWS Educational Assistant Repository

Download the project code from GitHub:

```bash
git clone https://github.com/awsstudygroup/AWS-Educational-Assistant
cd AWS-Educational-Assistant
```

#### 5. Install Required Python Packages

Make sure to install the dependencies listed in the `requirements.txt` file:

```bash
pip3 install -r requirements.txt
```

This will install libraries like `streamlit`, `boto3`, `langchain`, and others needed to run the application.

#### 6. Run the Streamlit Application

Once the dependencies are installed, launch the Streamlit app:

```bash
streamlit run Home.py --server.port 8080
```

This will start the web app on port `8080`. You can access the interface by navigating to `http://localhost:8080` in your browser.

---

### Additional Resources

- **Amazon Bedrock Documentation**: Learn more about Bedrock’s capabilities and supported models.
  - [Amazon Bedrock](https://aws.amazon.com/bedrock/)

- **Introduction to Prompt Design**: A guide on effective prompt engineering for Claude 3.
  - [Introduction to Prompt Design](https://docs.anthropic.com/claude/docs/introduction-to-prompt-design)

- **Claude 3 Model Card**: Detailed information on the Claude 3 model, including its architecture and usage guidelines.
  - [Claude 3 Model Card](https://www-cdn.anthropic.com/de8ba9b01c9ab7cbabf5c33b80b7bbc618857627/Model_Card_Claude_3.pdf)
