import os
import sys
import json
from dataclasses import dataclass
from typing import Generator

import boto3
from botocore.config import Config
from dotenv import load_dotenv
from langchain.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from langchain_community.chat_models.bedrock import BedrockChat
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.security_utils import sanitize_input

load_dotenv()


@dataclass(frozen=True)
class BedrockConfig:
    model_id: str = os.environ.get("AWS_BEDROCK_MODEL_ID", "anthropic.claude-sonnet-4-6")
    region: str = os.environ.get("AWS_REGION", "us-east-1")
    guardrail_id: str = os.environ.get("BEDROCK_GUARDRAIL_ID", "")
    guardrail_version: str = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT")


_config = BedrockConfig()
_client = boto3.client(
    "bedrock-runtime",
    region_name=_config.region,
    config=Config(read_timeout=120),
)


def _build_guardrail_config() -> dict | None:
    if not _config.guardrail_id:
        return None
    return {
        "guardrailIdentifier": _config.guardrail_id,
        "guardrailVersion": _config.guardrail_version,
        "trace": "enabled",
    }


def _converse_stream(system_prompt: str, user_text: str) -> Generator[str, None, None]:
    sanitized = sanitize_input(user_text)
    messages = [
        {
            "role": "user",
            "content": [
                {"guardContent": {"text": {"text": sanitized}}}
            ],
        }
    ]
    kwargs: dict = {
        "modelId": _config.model_id,
        "system": [{"text": system_prompt}],
        "messages": messages,
        "inferenceConfig": {"maxTokens": 2000, "temperature": 0.0, "topP": 1.0},
    }
    guardrail = _build_guardrail_config()
    if guardrail:
        kwargs["guardrailConfig"] = guardrail

    try:
        response = _client.converse_stream(**kwargs)
        for event in response.get("stream", []):
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"].get("delta", {})
                text = delta.get("text")
                if text:
                    yield text
    except Exception as e:
        yield f"\n[Error: {e}]"


def call_claude_sonet_stream(prompt: str) -> Generator[str, None, None]:
    return _converse_stream("You are a helpful assistant.", prompt)


def rewrite_document(input_text: str) -> Generator[str, None, None]:
    system = "Your name is good writer. You need to rewrite content provided by the user."
    return _converse_stream(system, str(input_text))


def summary_stream(input_text: str) -> Generator[str, None, None]:
    system = "Based on the provided context, create summary of the final content. Provide summary in Vietnamese."
    return _converse_stream(system, str(input_text))


def query_document(question: str, docs: str) -> Generator[str, None, None]:
    system = "Answer the user's question based on the provided document content."
    user_text = f"Content:\n{docs}\n\nQuestion: {question}"
    return _converse_stream(system, user_text)


def create_questions(input_text: str, callback=None) -> Generator[str, None, None]:
    system = """You are an expert in creating high-quality multiple-choice questions and answer pairs based on a given context. Based on the given context, you should:
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
MAKE SURE TO INCLUDE THE FULL CORRECT ANSWER AT THE END, NO EXPLANATION NEEDED."""
    prompt = f"Based on the provided context, create 10 multiple-choice questions and answer pairs:\n{input_text}"
    return _converse_stream(system, prompt)


def suggest_writing_document(input_text: str) -> Generator[str, None, None]:
    system = "Your name is good writer. You need to suggest and correct mistakes in the essay provided by the user."
    return _converse_stream(system, str(input_text))


def search(question: str, callback) -> dict:
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id="EWVHJIY9AS",
        retrieval_config={"vectorSearchConfiguration": {
            "numberOfResults": 3,
            "overrideSearchType": "SEMANTIC",
        }},
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

    max_query_length = 1000
    truncated_question = question[:max_query_length] if len(question) > max_query_length else question
    bedrock_client = boto3.client("bedrock-runtime", region_name=_config.region)

    model_kwargs_claude = {"temperature": 0.5, "top_p": 1}
    llm = BedrockChat(
        model_id=_config.model_id,
        client=bedrock_client,
        model_kwargs=model_kwargs_claude,
        streaming=True,
        callbacks=[callback],
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("input"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, question_answer_chain)

    return chain.invoke({"input": truncated_question})
