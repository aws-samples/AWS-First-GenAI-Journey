import os
import boto3, json
from dotenv import load_dotenv
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import RetrievalQA
from langchain_community.chat_models import BedrockChat
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def call_claude_sonet_stream(prompt):

    prompt_config = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
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

    body = json.dumps(prompt_config)

    modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    accept = "application/json"
    contentType = "application/json"

    bedrock = boto3.client(service_name="bedrock-runtime")  
    response = bedrock.invoke_model_with_response_stream(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )

    stream = response['body']
    if stream:
        for event in stream:
            chunk = event.get('chunk')
            if chunk:
                 delta = json.loads(chunk.get('bytes').decode()).get("delta")
                 if delta:
                     yield delta.get("text")    
                     
                     
                     

def rewrite_document(input_topic, subject_area, audience_level):
    """
    Generates a prompt to create educational content using an AI model.

    Parameters:
    input_topic (str): The specific topic for the lesson.
    subject_area (str): The subject area related to the topic.
    audience_level (str): The target audience level (e.g., high school students, professionals).

    Returns:
    str: The formatted prompt ready to be used with the AI model.
    """
    
    # Template for the AI prompt with placeholders for dynamic content
    prompt_template = (
        "You are an expert educator with deep knowledge in {subject_area}. "
        "Your task is to create an engaging and informative lesson on the topic of '{input_topic}'. "
        "The content should be suitable for {audience_level}, and it should include the following elements:\n\n"
        "1. **Introduction**: Start with an introduction that explains the importance of the topic and how it relates to the broader subject area.\n\n"
        "2. **Key Concepts**: Clearly define and explain the key concepts, theories, or principles related to the topic. Use simple language and examples to ensure understanding.\n\n"
        "3. **Practical Applications**: Describe how these concepts can be applied in real-world scenarios. Provide at least two examples or case studies.\n\n"
        "4. **Common Misconceptions**: Identify any common misconceptions about the topic and provide clarifications to correct these misunderstandings.\n\n"
        "5. **Summary**: End with a summary that recaps the main points covered in the lesson, highlighting the most important takeaways.\n\n"
        "6. **Further Reading**: Suggest additional resources or readings for students who want to explore the topic in more depth.\n\n"
        "Please write the content in a clear, concise, and engaging manner, suitable for the specified audience. Ensure that the information is accurate and up-to-date.\n\n"
        "Here is the topic for the lesson:\n"
        "{input_topic}\n\n"
        "You may begin your lesson."
    )
    
    # Format the prompt with the provided parameters
    formatted_prompt = prompt_template.format(
        subject_area=subject_area,
        input_topic=input_topic,
        audience_level=audience_level
    )
    
    # Call the AI model using the generated prompt
    return call_claude_sonet_stream(formatted_prompt)

# Example usage:
# topic = "The Impact of Climate Change on Global Ecosystems"
# subject = "Environmental Science"
# audience = "high school students"
# educational_content = create_educational_content(topic, subject, audience)



def summary_stream(input_text, summary_length="medium", detail_level="medium", use_case="general"):
    """
    Summarizes the provided lecture or academic paper content using the Claude Sonnet model.

    Args:
        input_text (str): The text content of the lecture or paper to be summarized.
        summary_length (str): The desired length of the summary ('short', 'medium', 'long').
        detail_level (str): The desired level of detail in the summary ('high', 'medium').
        use_case (str): The specific use case for the summary ('study', 'exam preparation', 'research', 'general').

    Returns:
        str: The customized summarized content.
    """
    length_descriptions = {
        "short": "brief and to the point, capturing only the most essential details",
        "medium": "concise but comprehensive, covering key concepts and important points",
        "long": "detailed and thorough, including most of the significant aspects"
    }

    detail_descriptions = {
        "high": "with a focus on deep analysis and critical points",
        "medium": "covering all important elements with a balanced level of detail"
    }

    use_case_descriptions = {
        "study": "emphasizing key points and concepts to aid in understanding and retention",
        "exam preparation": "focusing on potential exam questions and critical facts for quick revision",
        "research": "highlighting in-depth analysis, methodologies, and key findings",
        "general": "providing a well-rounded summary suitable for a general audience"
    }

    prompt = (
        f"Please summarize the following academic content with the following specifications:\n"
        f"Length: {length_descriptions.get(summary_length, 'medium')}\n"
        f"Detail Level: {detail_descriptions.get(detail_level, 'medium')}\n"
        f"Use Case: {use_case_descriptions.get(use_case, 'general')}\n\n"
        f"Content:\n{input_text}\n\n"
        f"Summary:"
    )
    return call_claude_sonet_stream(prompt)


def query_document(question, docs):
    prompt = """
    Human: You are an educational assistant specializing in helping students understand and review lecture content. Below is the content of a lecture document:

    <lecture_content>
    """ + str(docs) + """
    </lecture_content>
    
    Please review the content and provide a clear and concise answer to the following question:

    Question: """ + question + """
    
    Answer based solely on the content provided and ensure that your response is accurate and relevant to the educational context.

    \n\nAssistant:"""

    # Get the generator from call_claude_sonet_stream
    response_generator = call_claude_sonet_stream(prompt)

    # Retrieve the complete response by iterating over the generator and filtering out None values
    response = "".join([chunk for chunk in response_generator if chunk is not None])

    return response



def create_questions(input_text): 
    system_prompt = """You are an expert in creating high-quality multiple-choice questions and answer pairs based on a given context. Your task is to carefully analyze the provided content and generate questions that assess comprehension, critical thinking, and application of the material. Ensure that each question is clear, concise, and aligned with the key concepts of the context. Additionally, provide one correct answer along with three plausible distractors to challenge the learner's understanding. The questions should vary in difficulty and cover different aspects of the content, including factual recall, interpretation, and synthesis, you should:
    1. Create thought-provoking multiple-choice questions that assess the reader's understanding of the context. 
    2. Ensure the questions are clear, concise, and relevant.
    3. Provide logical and contextually relevant answer options.

    The format for multiple-choice questions and answer pairs should be as follows: 
        1) Question: 

        A) Option 1

        B) Option 2 

        C) Option 3 
        
        D) Option 4

        Answer: A) Option 1

    Continue generating additional questions and answer pairs as needed.

    MAKE SURE TO INCLUDE THE FULL CORRECT ANSWER AT THE END, NO EXPLANATION NEEDED:"""
    
    prompt = f"""{system_prompt} Based on the provided context, create 20 multiple-choice questions and answer pairs
    \n\nHuman: here is the content:
    <text>""" + str(input_text) + """</text>
    \n\nAssistant: """
    
    return call_claude_sonet_stream(prompt)


def suggest_writing_document(input_text): 
    prompt = """
    Your task is to act as an experienced instructional designer and educator. You will review the provided content to prepare a comprehensive and engaging syllabus. The syllabus should be well-organized, clear, and aligned with best practices in syllabus design. Consider the following elements:

    1. **Course Overview:** Provide a concise introduction to the course, including objectives, key topics, and the course's relevance to the students.
    2. **Learning Outcomes:** Clearly define what students will learn and be able to do by the end of the course.
    3. **Course Structure:** Break down the course into modules or units, outlining the content covered in each week or session.
    4. **Assessment Methods:** Detail how students will be assessed, including assignments, quizzes, exams, projects, and participation.
    5. **Course Materials:** List the required and recommended readings, textbooks, and any other resources students will need.
    6. **Policies and Expectations:** State the course policies, such as attendance, participation, academic integrity, and grading criteria.
    7. **Schedule:** Provide a tentative schedule that includes important dates for lectures, assignments, exams, and other activities.
    8. **Engagement:** Ensure the syllabus is engaging and motivating, setting a positive tone for the course.

    Content to review:
    <text>""" + str(input_text) + """</text>

    Your response should include specific suggestions for improving the syllabus, explanations for any revisions, and additional tips for enhancing the overall quality and effectiveness of the syllabus.

    Assistant: 
    """
    return call_claude_sonet_stream(prompt)


def search(question, callback):
    # Initialize the retriever with the specified knowledge base and retrieval configuration
    retriever = AmazonKnowledgeBasesRetriever(
        knowledge_base_id="7H2VGA3SDN",
        retrieval_config={"vectorSearchConfiguration": {"numberOfResults": 1}},
    )

    # Define model-specific parameters for Claude
    model_kwargs_claude = {"max_tokens": 2000}
    
    # Initialize the BedrockChat LLM with streaming enabled
    llm = BedrockChat(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        model_kwargs=model_kwargs_claude,
        streaming=True,
        callbacks=[callback]
    )

    # Set up the RetrievalQA chain using the retriever and LLM, including source documents in the return
    chain = RetrievalQA.from_chain_type(
        llm=llm, 
        retriever=retriever, 
        return_source_documents=True
    )
    
    # Execute the chain with the provided question and return the result
    return chain.invoke(question)