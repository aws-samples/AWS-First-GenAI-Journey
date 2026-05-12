import streamlit as st
import boto3

st.set_page_config(page_title="AWS Smart Email Assistant", page_icon="📧")
st.title("📧 AWS Smart Email Assistant")

SYSTEM_PROMPTS = {
    "Draft Reply": "You are a professional email assistant. Draft a polite, concise reply to the email thread provided. Match the tone of the original email.",
    "Summarize Thread": "You are an email summarizer. Provide a brief, structured summary of the email thread highlighting key points, decisions, and participants.",
    "Extract Action Items": "You are a task extraction assistant. Extract all action items from the email thread. List each with the responsible person and deadline if mentioned.",
    "Translate": "You are a translator. Translate the email thread to the target language specified by the user. Preserve formatting and tone.",
}

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

email_thread = st.text_area("Paste your email thread:", height=250, placeholder="Paste the email conversation here...")
action = st.selectbox("Choose an action:", list(SYSTEM_PROMPTS.keys()))

target_lang = ""
if action == "Translate":
    target_lang = st.text_input("Target language:", value="Spanish")

if st.button("Process", type="primary"):
    if not email_thread.strip():
        st.warning("Please paste an email thread first.")
    else:
        user_msg = email_thread
        if action == "Translate":
            user_msg += f"\n\nTranslate to: {target_lang}"

        with st.spinner("Processing..."):
            try:
                response = bedrock.converse(
                    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                    messages=[{"role": "user", "content": [{"text": user_msg}]}],
                    system=[{"text": SYSTEM_PROMPTS[action]}],
                    inferenceConfig={"maxTokens": 1024, "temperature": 0.3},
                )
                result = response["output"]["message"]["content"][0]["text"]
                st.subheader("Result")
                st.markdown(result)
                st.code(result, language=None)
                st.caption("👆 Click the copy icon on the code block above to copy the result.")
            except Exception as e:
                st.error(f"Error: {e}")
