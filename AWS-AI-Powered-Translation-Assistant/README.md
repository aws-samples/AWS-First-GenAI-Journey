# **Technical Guide for AWS-AI-Powered-Translation-Assistant**

## **Introduction**

This guide provides a step-by-step walkthrough for setting up and using the **AWS-AI-Powered-Translation-Assistant**. The application leverages **Amazon Bedrock** and **Generative AI** for text translation across multiple languages, providing three user interfaces: text, chat, and file-based translations.

## **Goal**

The goal is to create a translation **Proof of Concept (POC)** using **Amazon Bedrock**. The web-based frontend enables users to translate text, chat in real-time, and upload files for translation.

## **System Architecture Overview**

The system is designed with three primary translation modes:
1. **Text Input**: Translate text with feedback on accuracy and fluency.
2. **Chat**: Provide real-time translation for conversational input.
3. **File Upload**: Upload a text file and receive its translated version.

Each interface interacts with **Amazon Bedrock** for translation, using **Streamlit** for the frontend.

---

## **How to Use This Repository**

### **Prerequisites**
- **Amazon Bedrock**: Ensure access via AWS CLI, with credentials set up for interacting with Bedrock models.
- **Python 3.10**: Install from [here](https://www.python.org/downloads/release/python-3100/).
- **AWS CLI**: Installed and configured with access to Amazon Bedrock.

### **Step 1: Clone the Repository**

Clone the GitHub repository to your local environment:

```bash
git clone https://github.com/repo.git
cd aws-ai-powered-translation-assistant
```

Key files include:
- **Text.py, Chat.py, File.py**: Streamlit frontends for text, chat, and file translation.
- **amazon_bedrock_translation.py**: Logic for interacting with Amazon Bedrock's AI models.
- **requirements.txt**: Lists required dependencies.

---

### **Step 2: Set Up a Virtual Environment**

Navigate to the repository folder and set up a virtual environment:

```bash
pip install virtualenv
python3.10 -m venv venv
```

Activate the virtual environment:

- For Linux/MacOS:
  ```bash
  source venv/bin/activate
  ```
- For Windows:
  ```bash
  venv\Scripts\activate
  ```

Install all necessary dependencies:

```bash
pip install -r requirements.txt
```

---

### **Step 3: Configure AWS Credentials and Region**

Configure the AWS CLI to work with Amazon Bedrock by creating a `.env` file in the root directory. Add the following details:

```bash
profile_name=<AWS_CLI_PROFILE_NAME>
```

Ensure your AWS CLI profile is properly configured and has Bedrock access. If you want to specify a different AWS region, adjust the Bedrock client in `prompt_finder_and_invoke_llm.py`:

```python
bedrock = boto3.client('bedrock-runtime', 'us-east-1', endpoint_url='https://bedrock-runtime.us-east-1.amazonaws.com')
```

---

### **Step 4: Customize Amazon Bedrock Models**

The application uses **Claude 3** by default, but you can modify the `modelId` in `amazon_bedrock_translation.py` to use other models:

```python
def llm_answer_generator(question_with_prompt):
    prompt = "Translation prompt"
    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": 8191,
        "temperature": 0,
        "top_k": 250,
        "top_p": 0.5,
        "stop_sequences": []
    })
    modelId = 'anthropic.claude-v2'  # Change this to any other Bedrock-supported model
    response = bedrock.invoke_model(body=body, modelId=modelId)
    response_body = json.loads(response.get('body').read())
    return response_body.get('completion')
```

Adjust the `modelId` to any Bedrock-supported model based on your preference.

---

### **Step 5: Running the Application**

Start the application using the following command:

```bash
streamlit run Text.py
```

This will launch the app in your browser, allowing you to test the text, chat, and file-based translation functionalities.

---

## **Application Interfaces**

### **Text Input Interface**
1. Enter the text to be translated.
2. Select the source and target languages.
3. View the translated text and receive feedback on accuracy and fluency.

### **Chat Interface**
1. Input conversational text.
2. Select the target language for real-time translation.
3. Receive immediate translated responses.

### **File Upload Interface**
1. Upload a text file for translation.
2. Select the target language.
3. Download or view the translated file contents.

---

## **Conclusion**

This guide outlines the steps to set up and deploy the **AWS-AI-Powered-Translation-Assistant** using **Amazon Bedrock**. The application provides an interactive frontend for text, chat, and file translation, making it easy to extend or modify the POC. By following these steps, you can quickly spin up a working translation tool using AWS's powerful generative AI services.