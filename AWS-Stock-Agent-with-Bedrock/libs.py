import boto3, json
from dotenv import load_dotenv
from langchain.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from langchain_community.chat_models.bedrock import BedrockChat
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import RetrievalQA

load_dotenv()

def call_claude_sonet_stream(prompt):
    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "temperature": 0, 
        "top_k": 0,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    }

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

    bedrock = boto3.client(service_name="bedrock-runtime")  
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
                    
def rewrite_document(input_text): 
    prompt = """Your name is good writer. You need to rewrite content: 
        \n\nHuman: here is the content
        <text>""" + str(input_text) + """</text>
    \n\nAssistant: """
    return call_claude_sonet_stream(prompt)


def summary_stream(input_text):     
    prompt = f"""Based on the provided context, create summary of the final content. Provide summary in Vietnamese.
        \n\nHuman: here is the content
        <text>""" + str(input_text) + """</text>
    \n\nAssistant: """
    return call_claude_sonet_stream(prompt)

def query_document(question, docs): 
    prompt = """Human: here is the content:
        <text>""" + str(docs) + """</text>
        Question: """ + question + """ 
    \n\nAssistant: """

    return call_claude_sonet_stream(prompt)

def create_questions(input_text, callback): 
    system_prompt = """You are an expert in creating high-quality multiple-choice quesitons and answer pairs 
    based on a given context. Based on the given context (e.g a passage, a paragraph, or a set of information), you should:
    1. Come up with thought-provoking multiple-choice questions that assess the reader's understanding of the context. 
    2. The questions should be clear and concise.
    3. The answer options should be logical and relevant to the context.

    The multiple-choice questions and answer pairs should be in a bulleted list: 
        1) Question: 

        A) Option 1

        B) Option 2 

        C) Option 3 

        Answer: A) Option 1 

         
    Continue with additional questions and answer pairs as needed.

    MAKE SURE TO INCLUDE THE FULL CORRECT ANSWER AT THE END, NO EXPLANATION NEEDED:"""
    
    prompt = f"""{system_prompt}. Based on the provided context, create 10 multiple-choice questions and answer pairs
        \n\nHuman: here is the content
        <text>""" + str(input_text) + """</text>
    \n\nAssistant: """
    return call_claude_sonet_stream(prompt)

def suggest_writing_document(input_text): 
    prompt = """Your name is good writer. You need to suggest and correct mistake in the essay: 
        \n\nHuman: here is the content
        <text>""" + str(input_text) + """</text>
    \n\nAssistant: """
    return call_claude_sonet_stream(prompt)

def search(question, callback):
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id="EWVHJIY9AS",
        retrieval_config={"vectorSearchConfiguration": 
                          {"numberOfResults": 3,
                           'overrideSearchType': "SEMANTIC", # optional
                           }
                          },
    )

    system_prompt = """
        You are a financial advisor AI system with deep market insights. Impress all customers with your financial data 
        and market trends analysis. Investigate and analyze specific trading strategies, 
        technical analysis, and technical tools, or market structures. Provide a comprehensive overview of the chosen topic, 
        ensuring the explanation is both in-depth and understandable for traders of all levels. 
        Utilize your expertise and available market analysis tools to scan, filter, and evaluate potential assets for trading. 
        Once identified, create a comprehensive list with supporting data for each asset, indicating why it meets the criteria. 
        Ensure that all information is up-to-date and relevant to the current market conditions. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Provide your answer in Vietnamese.
        {context}
        """

    # Truncate the question if it's too long
    max_query_length = 1000
    truncated_question = question[:max_query_length] if len(question) > max_query_length else question
    bedrock_client = boto3.client('bedrock-runtime', region_name = 'us-east-1')

    model_kwargs_claude = { "temperature": 0.5, "top_p": 1}
    llm = BedrockChat(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",  # Updated model ID
        client=bedrock_client,
        model_kwargs=model_kwargs_claude,
        streaming=True,
        callbacks=[callback]
    )

    prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("input")
    ]
    )

    # Create the chain with the custom prompt
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, question_answer_chain)

    # Invoke the chain with the necessary inputs
    return chain.invoke( {
        "input": truncated_question  
    })

def searchOld(question, callback):
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id="EWVHJIY9AS",
        retrieval_config={"vectorSearchConfiguration": 
                          {"numberOfResults": 3,
                           'overrideSearchType': "SEMANTIC", # optional
                           }
                          },
    )
    system_prompt = """
        You are a financial advisor AI system with deep market insights. Impress all customers with your financial data 
        and market trends analysis. Investigate and analyze specific trading strategies, 
        technical analysis, and technical tools, or market structures. Provide a comprehensive overview of the chosen topic, 
        ensuring the explanation is both in-depth and understandable for traders of all levels. 
        Utilize your expertise and available market analysis tools to scan, filter, and evaluate potential assets for trading. 
        Once identified, create a comprehensive list with supporting data for each asset, indicating why it meets the criteria. 
        Ensure that all information is up-to-date and relevant to the current market conditions. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Provide your answer in Vietnamese.
        {context}
        """
    question = question
    query = f"""{system_prompt}. Based on the provided context, provide the answer to the following question:
    Question: {question}
    Answer: 
    """
    model_kwargs_claude = {"max_tokens": 2000}
    llm = BedrockChat(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
                      , model_kwargs=model_kwargs_claude
                      , streaming=True
                      , callbacks=[callback])

    chain = RetrievalQA.from_chain_type(
        llm=llm, retriever=retriever, return_source_documents=True
    )
    return chain.invoke(query)