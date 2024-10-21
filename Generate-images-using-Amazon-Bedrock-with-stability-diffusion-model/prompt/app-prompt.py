import streamlit as st
import boto3
from botocore.exceptions import ClientError

# Initialize AWS Bedrock client
client = boto3.client("bedrock-runtime", region_name="us-west-2")

# Define Claude 3 Sonnet model ID
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

# Function to call AWS Bedrock with user input
def generate_prompts(user_topic):
    positive_prompt = f"Generate a positive prompt for the topic: {user_topic}"
    negative_prompt = f"Generate a negative prompt to exclude undesirable aspects for the topic: {user_topic}"

    # Construct conversation input for Claude
    conversation = [
        {
            "role": "user",
            "content": [
                {"text": f"Generate two prompts. Positive prompt: {positive_prompt}. Negative prompt: {negative_prompt}"}
            ],
        }
    ]

    try:
        # Call Bedrock API
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens": 2000, "temperature": 0.7},
        )
        response_text = response["output"]["message"]["content"][0]["text"]
        return response_text

    except (ClientError, Exception) as e:
        return f"Error occurred: {e}"

# Streamlit UI
def main():
    # Sidebar for app info and navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("**Prompt Generator**")
    
    # Main title
    st.title("🎨 Auto Prompt Generator with Claude 3")

    # Description
    st.markdown("""
    Welcome to the Auto Prompt Generator! This tool uses AWS Bedrock with Claude 3 to generate **positive** and **negative** prompts for any topic.
    Simply enter a topic below, and let the AI create prompts for you.
    """)

    # User input for topic
    user_topic = st.text_input(
        label="Enter a topic:",
        placeholder="e.g., AI advancements in healthcare",
        help="Provide a topic or concept for which you want the AI to generate prompts."
    )

    # Button to generate prompts
    if st.button("Generate Positive & Negative Prompts"):
        if user_topic:
            # Display loading spinner while generating
            with st.spinner('Generating prompts...'):
                result = generate_prompts(user_topic)

            # Display result
            if "Error occurred" in result:
                st.error(result)
            else:
                st.success("Prompts generated successfully!")
                st.subheader("Generated Prompts:")
                st.write(result)
        else:
            st.warning("Please enter a topic to generate prompts.")

    # Add a footer for better UX
    st.markdown("---")
    st.markdown("Powered by [AWS Bedrock](https://aws.amazon.com/bedrock/) and **Claude 3**")

if __name__ == "__main__":
    main()
