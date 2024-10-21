from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
import streamlit as st
from streamlit_chat import message
import boto3
import json
from anthropic import Anthropic
import base

anthropic = Anthropic()

#knowledge_base_id=('EWVHJIY9AS'),
knowledge_base_id=('GDPSQICWNW'),
#modelId = "anthropic.claude-3-haiku-20240307-v1:0"
modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"

st.set_page_config(page_title="Tra cứu thông tin chứng khoán", page_icon="img/favicon.ico", layout="wide")
st.markdown(
  """
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
  """, 
  unsafe_allow_html=True
)

st.title('Tra cứu thông tin chứng khoán')

def count_tokens(text):
    return len(anthropic.get_tokenizer().encode(text))

base.init_home_state("RoboStock - Your 24/7 AI financial companion")
base.init_slidebar()
base.init_dialog()
base.init_animation()


def generate_response(prompt):
    bedrock = boto3.client(service_name="bedrock-runtime")  
    
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id = knowledge_base_id[0], 
        top_k = 5,
        retrieval_config = {
            "vectorSearchConfiguration": {
                "numberOfResults": 5, 
                'overrideSearchType': "SEMANTIC"
            }
        }
    )
    
    retrieved_docs = retriever.get_relevant_documents(prompt + " 2024")
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    conversation_history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state['messages']])

    query = f"""Human: {base.system_prompt}. Based on the provided context, provide the answer to the following question:
    <context>{context}</context>
    <conversation_history>{conversation_history}</conversation_history>
    <question>{prompt} </question>
    Remember, while you can offer analysis and insights, you should not make definitive predictions about future market movements or provide personalized financial advice.
    Assistant: 
    """
 
    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [
            {"role": "user", "content": query}
        ],
        "temperature": 0.7,
        "top_p": 1,
    }
    
    response = bedrock.invoke_model_with_response_stream(
        body=json.dumps(prompt_config),
        modelId=modelId,
        accept="application/json", 
        contentType="application/json"
    )

    stream = response['body']
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                chunk_obj = json.loads(chunk.get('bytes').decode())
                if 'delta' in chunk_obj:
                    delta_obj = chunk_obj.get('delta', None)
                    if delta_obj:
                        text = delta_obj.get('text', None)
                        yield text


if prompt := st.chat_input():
    st.session_state.show_animation = False
    st.session_state.messages.append({"role": "user", "content": prompt})
    base.right_message(st, prompt)

if st.session_state.messages[-1]["role"] != "assistant":
    st.session_state.show_animation = False
    with st.chat_message(
        "user",
        avatar="img/fcj.png",
    ):
        if prompt:
            response = generate_response(prompt)
            full_response = st.write_stream(response)
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)

