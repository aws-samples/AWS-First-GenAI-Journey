import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import boto3
import json

st.set_page_config(page_title="AWS GenAI Data Analyst", layout="wide")
st.title("📊 Chat with Your Data")

bedrock = boto3.client("bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1"))

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df.head())
    st.caption(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if question := st.chat_input("Ask a question about your data..."):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        columns_info = ", ".join([f"{c} ({df[c].dtype})" for c in df.columns])
        prompt = (
            f"You are a data analyst. Given a pandas DataFrame `df` with columns: {columns_info}\n"
            f"Write Python code using pandas to answer: {question}\n"
            "Rules:\n"
            "- Use only pandas and matplotlib\n"
            "- Store the final answer in a variable called `result`\n"
            "- If a chart is appropriate, create it with plt and call plt.tight_layout()\n"
            "- Return ONLY the Python code, no explanations or markdown fences"
        )

        response = bedrock.converse(
            modelId="anthropic.claude-sonnet-4-6",
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 1024, "temperature": 0.1},
        )

        code = response["output"]["message"]["content"][0]["text"].strip()
        code = code.removeprefix("```python").removeprefix("```").removesuffix("```").strip()

        with st.chat_message("assistant"):
            st.code(code, language="python")
            try:
                local_vars = {"df": df.copy(), "pd": pd, "plt": plt}
                exec(code, {"__builtins__": {}}, local_vars)

                if "result" in local_vars:
                    st.write("**Result:**")
                    st.write(local_vars["result"])

                fig = plt.gcf()
                if fig.get_axes():
                    st.pyplot(fig)
                plt.close("all")

            except Exception as e:
                st.error(f"Execution error: {e}")

            answer = f"```python\n{code}\n```"
            st.session_state.messages.append({"role": "assistant", "content": answer})
else:
    st.info("👆 Upload a CSV file to get started.")
