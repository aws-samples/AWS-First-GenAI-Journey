import boto3
from dotenv import load_dotenv
import logging
import json
import os
import asyncio
import aioboto3
import re

# Setting up a logger with default settings
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Load environment variables from the .env file into the environment
load_dotenv()
# Setting up the default boto3 session with a specified AWS profile name
boto3.setup_default_session(profile_name=os.getenv("profile_name"))

async def get_bedrock_client():
    """
    Asynchronously creates and returns a client for interacting with the Bedrock Runtime service.

    This function uses aioboto3, an asynchronous version of the AWS SDK for Python (Boto3), to create a client
    for the Bedrock Runtime service. It retrieves the AWS profile name and region name from environment variables.

    Returns:
        aioboto3.client: A client object for interacting with the Bedrock Runtime service.
    """
    
    if os.getenv("profile_name") is None:
        os.environ["profile_name"] = "default"
        os.environ["region_name"] = "us-east-1"
    
    # Create an aioboto3 session using the specified profile name
    session = aioboto3.Session(profile_name=os.getenv("profile_name"))
    # Asynchronously create a client for the Bedrock Runtime service
    async with session.client(
            service_name='bedrock-runtime',
            region_name=os.getenv("region_name"),

    ) as client:
        return client


async def model_execution(client, user_prompt, system_prompt):
    """
    Asynchronously executes a model using specified prompts, provided by each evaluation function
    and returns the score and evaluation summary.
    :param client: An aioboto3 client object for invoking Amazon Bedrock and the specific model.
    :param user_prompt: The user prompt used during model execution.
    :param system_prompt: The system prompt for the model execution and unique to the specific evaluation function.
    :return: A tuple containing the score of the evaluation and evaluation summary.
    """
    # Construct the content payload with user prompt
    content = [{
        "type": "text",
        "text": user_prompt
    }]
    # Construct the prompt object with model execution parameters, formatted for the Claue 3 Messages API
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }
    # Convert the prompt object to a JSON string
    prompt = json.dumps(prompt)
    # Invoke the model asynchronously with the provided prompt
    response = await client.invoke_model(
        body=prompt,
        modelId="anthropic.claude-sonnet-4-6",
        accept="application/json",
        contentType="application/json"
    )
    # Read the response body and parse it as JSON
    response_body = await response['body'].read()
    response_json = json.loads(response_body)
    # Extract the output text from the response
    output_text = response_json['content'][0]['text']
    # Extract score and evaluation summary from the output text
    score = parse_xml(output_text, "score").strip()
    evaluation_summary = parse_xml(output_text, "thoughts").strip()
    # Return the score and evaluation summary
    return score, evaluation_summary


def parse_xml(xml, tag):
    """
    Parse XML-like content to extract the value associated with a specific tag, handling one level of nested same tags.
    :param xml: The XML-like content as a string.
    :param tag: The tag whose value needs to be extracted.
    :return: The value associated with the specified tag or an empty string if the tag is not found.
    """
    try:
        # Construct a regex pattern to find content inside the specified tag,
        # This pattern attempts to skip over any nested tags of the same type.
        pattern = f'<{tag}>(?:<[^/]*?>.*?</[^>]*?>|[^<]*?)+</{tag}>'
        # Find the outermost tags first
        matches = re.findall(pattern, xml, re.DOTALL)
        if matches:
            # If there are matches, strip the outermost tag and find again to handle nested same tags
            clean_matches = []
            for match in matches:
                # Strip the outermost tag
                content = re.sub(f'^<{tag}>|</{tag}>$', '', match, flags=re.DOTALL)
                # Append cleaned content
                clean_matches.append(content)
            return " ".join(clean_matches).strip()
        return ""
    except re.error as e:
        # Return an empty string if a regex error occurs
        print(f"Regex error: {e}")
        return ""


async def eval_model_accuracy(model, summary, source_text):
    """
    Evaluates the accuracy of a model's summary based on a source text.

    :param model: The model being evaluated, specifically the model that generated the specific summary.
    :param summary: The summary generated by the model, that is being evaluated.
    :param source_text: The original source text extracted from the pdfs.
    :return: A tuple containing the score and evaluation summary.
    """
    # Constructing the system prompt providing instructions, the source text, and evaluation criteria to evaluate model accuracy
    system_prompt = f"""
As an AI evaluator, you will be given a source body of text and an AI model's attempt to summarize that text.
Evaluate the AI's summarization of the <source_body> provide a grade based on Accuracy
Evaluate the AI model's summary based on the provided <evaluation_criteria>
Only perform your evaluation based of the model's summary using the provided <evaluation_criteria>; other criteria (Completeness, Logical Flow, Paragraph and Sentence Structure, Conciseness, Clarity, Objectivity, and Tone) will be evaluated in a different method.
Respond with a score of 0-5 using the details in <evaluation_grading> as a guide



<evaluation_criteria>
1. Accuracy:
   - How well did the summary accurately represent the key information, facts, and details present in the source text.
   - Are there contradictions or factual errors in the summary when compared to the source text.
   - Does the summary include any misleading or inaccurate information that is not supported by the source text.
   - Are the Numerical data, proper nouns, and other specific details from the source text accurately represented in the summary.


</evaluation_criteria>

<evaluation_grading>
5 - Excellent:
Accuracy: The summary accurately captures the key points and factual information from the source text without any errors or misrepresentations.

4 - Very Good:
Accuracy: The summary is highly accurate, with only minor inaccuracies or misrepresentations that do not significantly impact the overall meaning.

3 - Good:
Accuracy: The summary is generally accurate, but there are a few noticeable inaccuracies or misrepresentations that may slightly distort the meaning.

2 - Fair:
Accuracy: The summary contains several inaccuracies or misrepresentations that distort the meaning of the source text to a moderate extent.

1 - Poor:
Accuracy: The summary is riddled with inaccuracies and misrepresentations, significantly distorting the meaning of the source text.

0 - Unacceptable:
Accuracy: The summary is completely inaccurate and bears no resemblance to the source text, misrepresenting the information entirely.

</evaluation_grading>


The source body of text that the summaries are based off of:
<source_body>
{source_text}
</source_body>

Evaluate and determine a score for the model's Accuracy. Include the reasoning for your choice in your thoughts

Return your thought process for scoring in <thoughts> xml tags concisely 
Return your score (0-5) in <score> xml tags
Make sure to only respond with a score of 0 through 5 for your response in <score>, no other text, only the numerical score


"""
    # Constructing the user prompt containing the model name and summary generated by the respective model to be evaluated
    user_prompt = f"""
<model>
{model}
</model>

model's summary to be evaluated:
<summary>
{summary}
</summary>

"""
    # Acquiring an asynchronous client for invoking the evaluation model
    async with await get_bedrock_client() as client:
        # Executing the model asynchronously with the constructed prompts
        result = await model_execution(client, user_prompt, system_prompt)
    # Returning the result of model execution
    return result


async def eval_model_completeness(model, summary, source_text):
    """
    Evaluates the completeness of a model's summary based on a source text.

    :param model: The model being evaluated, specifically the model that generated the specific summary.
    :param summary: The summary generated by the model, that is being evaluated.
    :param source_text: The original source text extracted from the pdfs.
    :return: A tuple containing the score and evaluation summary.
    """
    # Constructing the system prompt providing instructions, the source text, and evaluation criteria to evaluate model completeness
    system_prompt = f"""
As an AI evaluator, you will be given a source body of text and an AI model's attempt to summarize that text.
Evaluate the AI's summarization of the <source_body> provide a grade based on Completeness 
Evaluate the AI model's summary based on the provided <evaluation_criteria>
Only perform your evaluation based of the model's summary using the provided <evaluation_criteria>; other criteria (Accuracy, Logical Flow, Paragraph and Sentence Structure, Conciseness, Clarity, Objectivity, and Tone) will be evaluated in a different method.
Respond with a score of 0-5 using the details in <evaluation_grading> as a guide



<evaluation_criteria>


1. Completeness:
   - How well does the summary cover all the main points, key ideas, and essential information from the source text.
   - Does the summary capture all critical information or important details from the source text.
   - How well does the summary provide a comprehensive overview of the source text, capturing its essence and main themes.

</evaluation_criteria>

<evaluation_grading>
5 - Excellent:
Completeness: The summary covers all relevant aspects of the topic or question in an exhaustive and comprehensive manner. It leaves no significant gaps or omissions, addressing even nuanced or complex aspects of the subject matter.

4 - Very Good:
Completeness: The summary covers the vast majority of relevant aspects of the topic or question. While it may not delve into every minute detail, it provides a thorough and well-rounded understanding of the subject matter.

3 - Good:
Completeness: The summary covers the main points and essential aspects of the topic or question. However, it may lack some depth or overlook certain secondary or ancillary aspects of the subject matter.

2 - Fair:
Completeness: The summary addresses some of the relevant aspects of the topic or question but leaves out significant portions or key elements. The coverage is partial or incomplete.

1 - Poor:
Completeness: The summary provides only a superficial or cursory coverage of the topic or question, leaving out most of the relevant aspects or details. It lacks completeness and thoroughness.

0 - Unacceptable:
Completeness: The summary fails to address the topic or question adequately, leaving out essential information or aspects necessary for a complete understanding.

</evaluation_grading>


The source body of text that the summaries are based off of:
<source_body>
{source_text}
</source_body>

Evaluate and determine a score for the model's Completeness (as one). Include the reasoning for your choice in your thoughts

Return your thought process for scoring in <thoughts> xml tags concisely
Return your score (0-5) in <score> xml tags
Make sure to only respond with a score of 0 through 5 for your response in <score>, no other text, only the numerical score


"""
    # Constructing the user prompt containing the model name and summary generated by the respective model to be evaluated
    user_prompt = f"""
<model>
{model}
</model>

model's summary to be evaluated:
<summary>
{summary}
</summary>

"""
    # Acquiring an asynchronous client for invoking the evaluation model
    async with await get_bedrock_client() as client:
        # Executing the model asynchronously with the constructed prompts
        result = await model_execution(client, user_prompt, system_prompt)
    # Returning the result of model execution
    return result


async def eval_model_flow(model, summary, source_text):
    """
    Evaluates the logical flow of a model's summary based on a source text.

    :param model: The model being evaluated, specifically the model that generated the specific summary.
    :param summary: The summary generated by the model, that is being evaluated.
    :param source_text: The original source text extracted from the pdfs.
    :return: A tuple containing the score and evaluation summary.
    """
    # Constructing the system prompt providing instructions, the source text, and evaluation criteria to evaluate model flow
    system_prompt = f"""
As an AI evaluator, you will be given a source body of text and an AI model's attempt to summarize that text.
Evaluate the AI's summarization of the <source_body> provide a grade based on Logical Flow 
Evaluate the AI model's summary based on the provided <evaluation_criteria>
Only perform your evaluation based of the model's summary using the provided <evaluation_criteria>; other criteria (Completeness, Accuracy, Paragraph and Sentence Structure, Conciseness, Clarity, Objectivity, and Tone) will be evaluated in a different method.
Respond with a score of 0-5 using the details in <evaluation_grading> as a guide



<evaluation_criteria>
1. Logical Flow:
   - Does the summary present information in a logical, coherent, and easy-to-follow manner?
   - Is there a clear progression of ideas, with smooth transitions between points?
   - Does the organization of the summary mirror the structure and flow of the source text?
   - Is there a natural, intuitive flow that aids comprehension and maintains the intended meaning of the original text?
</evaluation_criteria>

<evaluation_grading>
5 - Excellent:
Logical Flow: The summary follows an exceptionally logical and coherent structure, mirroring the organization and progression of ideas in the source text. Transitions between points are seamless, and the flow of information is natural, easy to follow, and aids in comprehension.

4 - Very Good: 
Logical Flow: The summary maintains a largely logical and coherent flow, aligning well with the structure of the source text. While there may be a few minor instances of abrupt transitions or slight deviations from the original order of ideas, the overall flow is smooth and comprehensible.

3 - Good:
Logical Flow: The summary generally follows a logical progression, but there are occasional lapses or disruptions in the flow. While the main ideas are presented in a reasonable order, some transitions may be abrupt, or the organization may deviate slightly from the source text's structure.

2 - Fair:
Logical Flow: The summary exhibits a somewhat disjointed or inconsistent flow, with noticeable breaks or disruptions in the progression of ideas. The organization may not consistently mirror the structure of the source text, making it harder to follow the intended narrative or meaning.

1 - Poor:
Logical Flow: The summary lacks a clear logical flow or coherent structure, presenting information in a haphazard or disorganized manner. Transitions between points are abrupt or nonexistent, and the overall organization deviates significantly from the source text's structure, impeding comprehension.

0 - Unacceptable:
Logical Flow: The summary fails to establish any discernible logical flow or coherent progression of ideas. The information is presented in a completely disorganized and incoherent manner, rendering the summary difficult or impossible to follow.
</evaluation_grading>

The source body of text that the summaries are based off of:
<source_body>
{source_text}
</source_body>

Evaluate and determine a score for the model's Logical Flow. Include the reasoning for your choice in your thoughts

Return your thought process for scoring in <thoughts> xml tags concisely
Return your score (0-5) in <score> xml tags
Make sure to only respond with a score of 0 through 5 for your response for <score>, no other text, only the numerical score


"""
    # Constructing the user prompt containing the model name and summary generated by the respective model to be evaluated
    user_prompt = f"""
<model>
{model}
</model>

model's summary to be evaluated:
<summary>
{summary}
</summary>

"""
    # Acquiring an asynchronous client for invoking the evaluation model
    async with await get_bedrock_client() as client:
        # Executing the model asynchronously with the constructed prompts
        result = await model_execution(client, user_prompt, system_prompt)
    # Returning the result of model execution
    return result


async def eval_model_structure(model, summary, source_text):
    """
    Evaluates the structure of a model's summary based on a source text.

    :param model: The model being evaluated, specifically the model that generated the specific summary.
    :param summary: The summary generated by the model, that is being evaluated.
    :param source_text: The original source text extracted from the pdfs.
    :return: A tuple containing the score and evaluation summary.
    """
    # Constructing the system prompt providing instructions, the source text, and evaluation criteria to evaluate model structure
    system_prompt = f"""
As an AI evaluator, you will be given a source body of text and an AI model's attempt to summarize that text.
Evaluate the AI's summarization of the <source_body> provide a grade based on Paragraph and Sentence Structure
Evaluate the AI model's summary based on the provided <evaluation_criteria>
Only perform your evaluation based of the model's summary using the provided <evaluation_criteria>; other criteria (Completeness, Accuracy, Logical Flow, Conciseness, Clarity, Objectivity, and Tone) will be evaluated in a different method.
Respond with a score of 0-5 using the details in <evaluation_grading> as a guide



<evaluation_criteria>

1. Paragraph and Sentence Structure:
   - How well-structured and organized are the paragraphs in the summary?
   - Do the paragraphs flow logically and coherently, with clear transitions between ideas?
   - Are the sentences within each paragraph well-constructed, concise, and easy to understand?
   - Is there appropriate use of varied sentence structures (simple, compound, complex) to enhance readability and flow?
   - Are there any issues with run-on sentences, fragmented sentences, or awkward phrasing that hinder clarity?

</evaluation_criteria>

<evaluation_grading>
5 - Excellent:
Paragraph and Sentence Structure: The summary exhibits exceptional paragraph organization and sentence structure. Paragraphs are clearly delineated and flow seamlessly, with smooth transitions between ideas. Sentences within each paragraph are well-crafted, concise, and easy to comprehend. There is effective use of varied sentence structures, enhancing readability and flow. The writing is polished and error-free.

4 - Very Good:
Paragraph and Sentence Structure: The summary demonstrates strong paragraph organization and sentence structure. Paragraphs are well-structured, with appropriate transitions between ideas. Sentences within each paragraph are generally clear and well-constructed, with occasional minor issues. There is good use of varied sentence structures, contributing to overall readability. The writing is mostly error-free.

3 - Good:
Paragraph and Sentence Structure: The summary exhibits decent paragraph organization and sentence structure. Paragraphs are reasonably well-structured, though transitions between ideas could be improved. Sentences within each paragraph are generally understandable, but some may lack conciseness or clarity. There is some variation in sentence structures, but opportunities for improvement exist. Minor errors or awkward phrasing may be present but do not significantly impede understanding.

2 - Fair:
Paragraph and Sentence Structure: The summary shows fair paragraph organization and sentence structure. Paragraphs are loosely structured, with inconsistent or abrupt transitions between ideas. Sentences within each paragraph are often unclear, wordy, or convoluted, hindering readability. There is limited variation in sentence structures, leading to a repetitive or monotonous flow. Noticeable errors or awkward phrasing are present.

1 - Poor:
Paragraph and Sentence Structure: The summary displays poor paragraph organization and sentence structure. Paragraphs lack coherence and logical flow, with abrupt or confusing transitions between ideas. Sentences within each paragraph are frequently unclear, run-on, or fragmented, significantly impeding understanding. There is little to no variation in sentence structures, resulting in a choppy or monotonous reading experience. Numerous errors or awkward phrasing are present.

0 - Unacceptable:
Paragraph and Sentence Structure: The summary lacks any discernible paragraph organization or proper sentence structure. Paragraphs are disjointed or nonexistent, with no logical flow or transitions between ideas. Sentences within each paragraph are incomprehensible or severely flawed, rendering the text unintelligible. There is no variation in sentence structures, and the writing is riddled with errors and awkward phrasing, making it impossible to understand.

</evaluation_grading>

The source body of text that the summaries are based off of:
<source_body>
{source_text}
</source_body>

Evaluate and determine a score for the model's Paragraph and Sentence Structure. Include the reasoning for your choice in your thoughts

Return your thought process for scoring in <thoughts> xml tags concisely
Return your score (0-5) in <score> xml tags
Make sure to only respond with a score of 0 through 5 for your response in <score>, no other text, only the numerical score


"""
    # Constructing the user prompt containing the model name and summary generated by the respective model to be evaluated
    user_prompt = f"""
<model>
{model}
</model>

model's summary to be evaluated:
<summary>
{summary}
</summary>

"""
    # Acquiring an asynchronous client for invoking the evaluation model
    async with await get_bedrock_client() as client:
        # Executing the model asynchronously with the constructed prompts
        result = await model_execution(client, user_prompt, system_prompt)
    # Returning the result of model execution
    return result


async def eval_model_conciseness(model, summary, source_text):
    """
    Evaluates the conciseness of a model's summary based on a source text.

    :param model: The model being evaluated, specifically the model that generated the specific summary.
    :param summary: The summary generated by the model, that is being evaluated.
    :param source_text: The original source text extracted from the pdfs.
    :return: A tuple containing the score and evaluation summary.
    """
    # Constructing the system prompt providing instructions, the source text, and evaluation criteria to evaluate model conciseness
    system_prompt = f"""
As an AI evaluator, you will be given a source body of text and an AI model's attempt to summarize that text.
Evaluate the AI's summarization of the <source_body> provide a grade based on Conciseness
Evaluate the AI model's summary based on the provided <evaluation_criteria>
Only perform your evaluation based on the provided <evaluation_criteria>; other criteria (Completeness, Accuracy, Logical Flow, Paragraph and Sentence Structure, Clarity, Objectivity, and Tone) will be evaluated in a different method.
Respond with a score of 0-5 using the details in <evaluation_grading> as a guide



<evaluation_criteria>

1. Conciseness:
   - How effectively does the summary capture the main ideas and key information from the source text in a concise manner?
   - Is the summary free from unnecessary details, repetition, or irrelevant information?
   - Does the summary avoid wordiness and convey the essential points clearly and succinctly?
   - Is the length of the summary appropriate for the content, neither too long nor too short?
   - Does the summary strike a balance between being concise and retaining the necessary context and nuance?

</evaluation_criteria>

<evaluation_grading>
5 - Excellent:
Conciseness: The summary demonstrates exceptional conciseness in capturing the core ideas and essential information from the source text. It is highly effective in eliminating unnecessary details, repetition, and irrelevant information. The writing is succinct and avoids wordiness, conveying the key points clearly and concisely. The length of the summary is appropriate for the content, neither too long nor too short. The summary strikes an excellent balance between being concise and retaining the necessary context and nuance.

4 - Very Good:
Conciseness: The summary exhibits very good conciseness in capturing the main ideas and important information from the source text. It is proficient in avoiding unnecessary details, repetition, and irrelevant information. The writing is generally succinct and avoids wordiness, conveying the essential points clearly. The length of the summary is appropriate for the content, with only minor deviations. The summary maintains a very good balance between being concise and preserving the necessary context and nuance.

3 - Good:
Conciseness: The summary demonstrates good conciseness in capturing the core ideas and key information from the source text. It is reasonably effective in avoiding unnecessary details, repetition, and irrelevant information, though some minor instances may be present. The writing is generally concise, with occasional wordiness or lack of clarity. The length of the summary is mostly appropriate for the content, with some deviations. The summary maintains a decent balance between being concise and retaining the necessary context and nuance.

2 - Fair:
Conciseness: The summary exhibits fair conciseness in capturing the main ideas and important information from the source text. It has some difficulty avoiding unnecessary details, repetition, and irrelevant information, which are present throughout the summary. The writing is often wordy or lacks clarity, hindering conciseness. The length of the summary is somewhat appropriate for the content but could be improved. The summary struggles to strike a balance between being concise and retaining the necessary context and nuance.

1 - Poor:
Conciseness: The summary displays poor conciseness in capturing the core ideas and key information from the source text. It includes a significant amount of unnecessary details, repetition, and irrelevant information, which overwhelm the summary. The writing is excessively wordy and lacks clarity, making it difficult to discern the essential points. The length of the summary is inappropriate for the content, either too long or too short. The summary fails to find a balance between being concise and retaining the necessary context and nuance.

0 - Unacceptable:
Conciseness: The summary lacks any semblance of conciseness in capturing the main ideas and important information from the source text. It is overwhelmed by unnecessary details, excessive repetition, and irrelevant information, rendering the summary meaningless. The writing is excessively wordy and incomprehensible, making it impossible to discern the key points. The length of the summary is completely inappropriate for the content. The summary fails to retain any context or nuance, rendering it useless.

</evaluation_grading>

The source body of text that the summaries are based off of:
<source_body>
{source_text}
</source_body>

Evaluate and determine a score for the model's Conciseness. Include the reasoning for your choice in your thoughts

Return your thought process for scoring in <thoughts> xml tags concisely
Return your score (0-5) in <score> xml tags
Make sure to only respond with a score of 0 through 5 for your response in <score>, no other text, only the numerical score

"""
    # Constructing the user prompt containing the model name and summary generated by the respective model to be evaluated
    user_prompt = f"""
<model>
{model}
</model>

model's summary to be evaluated:
<summary>
{summary}
</summary>

"""
    # Acquiring an asynchronous client for invoking the evaluation model
    async with await get_bedrock_client() as client:
        # Executing the model asynchronously with the constructed prompts
        result = await model_execution(client, user_prompt, system_prompt)
    # Returning the result of model execution
    return result


async def eval_model_clarity(model, summary, source_text):
    """
    Evaluates the clarity of a model's summary based on a source text.

    :param model: The model being evaluated, specifically the model that generated the specific summary.
    :param summary: The summary generated by the model, that is being evaluated.
    :param source_text: The original source text extracted from the pdfs.
    :return: A tuple containing the score and evaluation summary.
    """
    # Constructing the system prompt providing instructions, the source text, and evaluation criteria to evaluate model clarity
    system_prompt = f"""
As an AI evaluator, you will be given a source body of text and an AI model's attempt to summarize that text.
Evaluate the AI's summarization of the <source_body> provide a grade based on Clarity
Evaluate the AI model's summary based on the provided <evaluation_criteria>
Only perform your evaluation based on the provided <evaluation_criteria>; other criteria (Completeness, Accuracy, Logical Flow, Paragraph and Sentence Structure, Conciseness, Objectivity, and Tone) will be evaluated in a different method.
Respond with a score of 0-5 using the details in <evaluation_grading> as a guide



<evaluation_criteria>
1. Clarity and Comprehensibility:
   - How easy is it to understand the key ideas and information presented in the summary?
   - Is the language used clear, concise, and free from ambiguity or confusing phrasing?
   - Does the summary accurately convey the main points and key details from the source text without introducing confusion or misinterpretation?
   - Are complex concepts or technical terms explained in a way that is easy for the target audience to comprehend?
   - Is the summary free from unnecessary jargon or overly complex language that could hinder understanding?
   - Is the summary clear, easy to understand, and human readable?
</evaluation_criteria>

<evaluation_grading>
5 - Excellent Clarity:
The summary is exceptionally clear and easy to understand. The language used is precise, concise, and free from ambiguity or confusing phrasing. The main ideas and key details from the source text are accurately and clearly conveyed without any misinterpretation or confusion. Complex concepts or technical terms are explained in a way that is accessible and comprehensible to the target audience. The summary avoids unnecessary jargon or overly complex language, ensuring optimal clarity.

4 - Very Good Clarity:
The summary demonstrates very good clarity and comprehensibility. The language used is generally clear and concise, with only minor instances of ambiguity or confusing phrasing. The main ideas and key details from the source text are accurately conveyed, with only a few minor points that may lack complete clarity. Complex concepts or technical terms are mostly well-explained, with occasional opportunities for further clarification. The summary largely avoids unnecessary jargon or overly complex language.

3 - Good Clarity:
The summary exhibits good clarity and comprehensibility. The language used is generally clear, although there may be some instances of ambiguity or confusing phrasing that could benefit from improvement. The main ideas and key details from the source text are conveyed accurately for the most part, but there may be a few points that lack complete clarity or risk misinterpretation. Complex concepts or technical terms are adequately explained, but some additional clarification may be needed. The summary may contain some unnecessary jargon or overly complex language that could hinder understanding for some readers.

2 - Fair Clarity:
The summary demonstrates fair clarity and comprehensibility. The language used is often unclear or ambiguous, with multiple instances of confusing phrasing that hinder understanding. The main ideas and key details from the source text are partially conveyed, but there are several points that lack clarity or risk misinterpretation. Complex concepts or technical terms are insufficiently explained, leaving room for confusion or misunderstanding. The summary contains a significant amount of unnecessary jargon or overly complex language that may impede comprehension for the target audience.

1 - Poor Clarity:
The summary exhibits poor clarity and comprehensibility. The language used is frequently unclear, ambiguous, or confusing, making it difficult to understand the main ideas and key details. The summary fails to accurately convey the core information from the source text, with numerous points lacking clarity or being misinterpreted. Complex concepts or technical terms are poorly explained or left unexplained, leading to confusion and misunderstanding. The summary is riddled with unnecessary jargon or overly complex language, significantly hindering comprehension for the target audience.

0 - Unacceptable Clarity:
The summary lacks any discernible clarity or comprehensibility. The language used is incomprehensible, with severe ambiguity and confusing phrasing throughout. The summary fails to convey the main ideas and key details from the source text accurately, rendering it meaningless or entirely unrelated to the original content. Complex concepts or technical terms are either absent or explained in an utterly confusing manner. The summary is filled with excessive jargon and overly complex language, making it impossible for the target audience to understand.
</evaluation_grading>

The source body of text that the summaries are based off of:
<source_body>
{source_text}
</source_body>

Evaluate and determine a score for the model's Clarity. Include the reasoning for your choice in your thoughts

Return your thought process for scoring <thoughts> xml tags
Return your score (0-5) in <score> xml tags
Make sure to only respond with a score of 0 through 5 for your response in <score>, no other text, only the numerical score

"""
    # Constructing the user prompt containing the model name and summary generated by the respective model to be evaluated
    user_prompt = f"""
<model>
{model}
</model>

model's summary to be evaluated:
<summary>
{summary}
</summary>

"""
    # Acquiring an asynchronous client for invoking the evaluation model
    async with await get_bedrock_client() as client:
        # Executing the model asynchronously with the constructed prompts
        result = await model_execution(client, user_prompt, system_prompt)
    # Returning the result of model execution
    return result


async def eval_model_objectivity(model, summary, source_text):
    """
    Evaluates the objectivity of a model's summary based on a source text.

    :param model: The model being evaluated, specifically the model that generated the specific summary.
    :param summary: The summary generated by the model, that is being evaluated.
    :param source_text: The original source text extracted from the pdfs.
    :return: A tuple containing the score and evaluation summary.
    """
    # Constructing the system prompt providing instructions, the source text, and evaluation criteria to evaluate model objectivity
    system_prompt = f"""
As an AI evaluator, you will be given a source body of text and an AI model's attempt to summarize that text.
Evaluate the AI's summarization of the <source_body> provide a grade based on Objectivity
Evaluate the AI model's summary based on the provided <evaluation_criteria>
Only perform your evaluation based on the provided <evaluation_criteria>; other criteria (Completeness, Accuracy, Logical Flow, Paragraph and Sentence Structure, Conciseness, Clarity, and Tone) will be evaluated in a different method.
Respond with a score of 0-5 using the details in <evaluation_grading> as a guide



<evaluation_criteria>
Objectivity:
- Does the summary present information objectively, without introducing personal biases, opinions, or judgments not present in the source text?
- Are subjective statements or claims in the source text accurately represented in the summary, without exaggeration or diminishment?
- Is the language used in the summary neutral and impartial, avoiding loaded or emotionally charged words that could influence the reader's perception?
- If the source text presents multiple perspectives or viewpoints, does the summary represent them fairly and accurately, without favoring or dismissing any particular stance?
- Are any factual errors or misrepresentations of information from the source text present in the summary?
</evaluation_criteria>

<evaluation_grading>
5 - Excellent:
Objectivity: The summary presents information from the source text in an entirely objective and impartial manner. It accurately reflects the content, tone, and multiple perspectives (if present) without introducing personal biases, opinions, or judgments. The language used is neutral and factual, devoid of loaded or emotionally charged words that could sway the reader's perception. There are no factual errors or misrepresentations of information from the source text.

4 - Very Good:
Objectivity: The summary maintains a high degree of objectivity, accurately representing the content and tone of the source text without significant bias or personal opinions. While largely impartial, there may be minor instances of slightly loaded language or a slight favoring of one perspective over others, but these do not significantly impact the overall neutrality of the summary. There are no major factual errors or misrepresentations.

3 - Good:
Objectivity: The summary generally presents information objectively, but there are occasional instances of subjective language, personal opinions, or biases that are not present in the source text. Multiple perspectives may be represented, but there is a noticeable favoring of one viewpoint over others. While there are no major factual errors, there may be some minor misrepresentations or exaggerations of information from the source text.

2 - Fair:
Objectivity: The summary displays a lack of objectivity, with frequent instances of subjective language, personal opinions, and biases not present in the source text. Multiple perspectives may be presented, but one viewpoint is clearly favored or dismissed. There are some factual errors or misrepresentations of information from the source text that impact the accuracy of the summary.

1 - Poor:
Objectivity: The summary is highly subjective and biased, with a significant portion of the content reflecting personal opinions, judgments, or exaggerations not present in the source text. Multiple perspectives are either not represented or are unfairly dismissed or misrepresented. There are numerous factual errors or misrepresentations of information from the source text, leading to a distorted or inaccurate summary.

0 - Unacceptable:
Objectivity: The summary is entirely subjective and opinionated, bearing little resemblance to the factual content or tone of the source text. Multiple perspectives are disregarded or grossly misrepresented. The summary is riddled with factual errors, misrepresentations, and biased language, rendering it an unreliable representation of the source material.
</evaluation_grading>

The source body of text that the summaries are based off of:
<source_body>
{source_text}
</source_body>

Evaluate and determine a score for the model's Objectivity. Include the reasoning for your choice in your thoughts

Return your thought process for scoring in <thoughts> xml tags concisely
Return your score (0-5) in <score> xml tags
Make sure to only respond with a score of 0 through 5 for your response in <score>, no other text, only the numerical score

"""
    # Constructing the user prompt containing the model name and summary generated by the respective model to be evaluated
    user_prompt = f"""
<model>
{model}
</model>

model's summary to be evaluated:
<summary>
{summary}
</summary>

"""
    # Acquiring an asynchronous client for invoking the evaluation model
    async with await get_bedrock_client() as client:
        # Executing the model asynchronously with the constructed prompts
        result = await model_execution(client, user_prompt, system_prompt)
    # Returning the result of model execution
    return result


async def eval_model_tone(model, summary, source_text):
    """
    Evaluates the tone of a model's summary based on a source text.

    :param model: The model being evaluated, specifically the model that generated the specific summary.
    :param summary: The summary generated by the model, that is being evaluated.
    :param source_text: The original source text extracted from the pdfs.
    :return: A tuple containing the score and evaluation summary.
    """
    # Constructing the system prompt providing instructions, the source text, and evaluation criteria to evaluate model tone
    system_prompt = f"""
As an AI evaluator, you will be given a source body of text and an AI model's attempt to summarize that text.
Evaluate the AI's summarization of the <source_body> provide a grade based on Tone Consistency 
Evaluate the AI model's summary based on the provided <evaluation_criteria>
Only perform your evaluation based on the provided <evaluation_criteria>; other criteria (Completeness, Accuracy, Logical Flow, Paragraph and Sentence Structure, Conciseness, Clarity, and Objectivity) will be evaluated in a different method.
Respond with a score of 0-5 using the details in <evaluation_grading> as a guide



<evaluation_criteria>

1. Tone Consistency:
   - Is the overall tone of the summary consistent with the source text?
   - Does the summary maintain a similar level of formality, emotion, or attitude as the original content?
   - Are there any shifts in tone within the summary that seem out of place or inconsistent?
   - Does the summary capture the intended tone and mood conveyed in the source text?
   - If the source text has a neutral or objective tone, does the summary maintain that impartial perspective?
   - If the source text has a more subjective or emotional tone, does the summary accurately reflect that tone without being overly exaggerated or understated?

</evaluation_criteria>

<evaluation_grading>
5 - Excellent:
Tone Consistency: The summary exhibits exceptional consistency in tone with the source text. The overall level of formality, emotion, or attitude is maintained throughout, accurately reflecting the intended tone and mood of the original content. There are no shifts or inconsistencies in tone within the summary. If the source text has a neutral or objective tone, the summary maintains that impartial perspective. If the source text has a more subjective or emotional tone, the summary accurately captures and conveys that tone without being overly exaggerated or understated.

4 - Very Good:
Tone Consistency: The summary demonstrates very good consistency in tone with the source text. The overall level of formality, emotion, or attitude is largely maintained, with only minor deviations that do not significantly impact the intended tone and mood. There may be a few slight shifts in tone within the summary, but they are not out of place. If the source text has a neutral or objective tone, the summary generally maintains that impartial perspective. If the source text has a more subjective or emotional tone, the summary accurately reflects that tone, with occasional minor instances of exaggeration or understatement.

3 - Good:
Tone Consistency: The summary exhibits good consistency in tone with the source text. The overall level of formality, emotion, or attitude is reasonably maintained, though there may be a few noticeable deviations or inconsistencies in tone. There are some shifts in tone within the summary, but they do not significantly detract from the intended tone and mood. If the source text has a neutral or objective tone, the summary may occasionally veer into a more subjective perspective. If the source text has a more subjective or emotional tone, the summary may at times exaggerate or understate that tone.

2 - Fair:
Tone Consistency: The summary shows fair consistency in tone with the source text. The overall level of formality, emotion, or attitude is inconsistently maintained, with several noticeable deviations or inconsistencies in tone. There are frequent shifts in tone within the summary that may seem out of place or . If the source text has a neutral or objective tone, the summary often adopts a subjective perspective. If the source text has a more subjective or emotional tone, the summary frequently exaggerates or understates that tone.

1 - Poor:
Tone Consistency: The summary displays poor consistency in tone with the source text. The overall level of formality, emotion, or attitude is rarely maintained, with significant deviations or inconsistencies in tone throughout. There are numerous  shifts in tone within the summary that seem out of place or inappropriate. If the source text has a neutral or objective tone, the summary is predominantly subjective or opinionated. If the source text has a more subjective or emotional tone, the summary either greatly exaggerates or severely understates that tone.

0 - Unacceptable:
Tone Consistency: The summary lacks any discernible consistency in tone with the source text. The overall level of formality, emotion, or attitude bears no resemblance to the intended tone and mood of the original content. The tone within the summary is wildly inconsistent, with constant  shifts that make it impossible to establish a coherent tone. Regardless of whether the source text has a neutral or subjective tone, the summary fails to capture or convey any semblance of the appropriate tone.

</evaluation_grading>

The source body of text that the summaries are based off of:
<source_body>
{source_text}
</source_body>

Evaluate and determine a score for the model's Tone Consistency . Include the reasoning for your choice in your thoughts

Return your thought process for scoring in <thoughts> xml tags concisely
Return your score (0-5) in <score> xml tags
Make sure to only respond with a score of 0 through 5 for your response in <score>, no other text, only the numerical score

"""
    # Constructing the user prompt containing the model name and summary generated by the respective model to be evaluated
    user_prompt = f"""
<model>
{model}
</model>

model's summary to be evaluated:
<summary>
{summary}
</summary>

"""
    # Acquiring an asynchronous client for invoking the evaluation model
    async with await get_bedrock_client() as client:
        # Executing the model asynchronously with the constructed prompts
        result = await model_execution(client, user_prompt, system_prompt)
    # Returning the result of model execution
    return result


async def eval_model_task(model, summary, source_text, task, evaluation_criteria, evaluation_grading):
    """
    Evaluates the task of a model's summary based on a source text.

    :param model: The model being evaluated, specifically the model that generated the specific summary.
    :param summary: The summary generated by the model, that is being evaluated.
    :param source_text: The original source text extracted from the pdfs.
    :return: A tuple containing the score and evaluation summary.
    """


    # Constructing the system prompt providing instructions, the source text, and evaluation criteria to evaluate model task
    system_prompt = f"""
As an AI evaluator, you will be provided the task/instructions that were given to an AI model, and the AI model's attempt to perform to perform that task
Evaluate the how well the AI's summary followed the tasks in the <prompt_instructions> in the creation of the summary and provide a grade
Use the provided <evaluation_criteria> to evaluate the AI model's attempt at a summary
Only perform your evaluation based on how well the model followed the given tasks; other criteria (Completeness, Accuracy, Logical Flow, Paragraph and Sentence Structure, Conciseness, Clarity, Tone, and Objectivity) will be evaluated in a different method.
Respond with a score of 0-5 using the details in <evaluation_grading> as a guide
Be fair but critical in your assessment 

If asked to count the number of sentences or paragraphs, use the following rules:
- A sentence should end with a period (.), exclamation mark (!), or question mark (?).
- Decimal points (e.g., 1.5), colons (:), semi-colons (;), and commas (,) should not be considered as sentence terminators.


The task that was provided to the AI model:
<prompt_instructions>
{task}
</prompt_instructions>


<evaluation_criteria>
{evaluation_criteria}
</evaluation_criteria>

<evaluation_grading>
{evaluation_grading}
</evaluation_grading>

The AI model was given this body of text to operate on:
<source_body>
{source_text}
</source_body>

Evaluate and determine a score for the model's Adherence to the Task. Include the reasoning for your choice in your thoughts

Return your thought process for scoring in <thoughts> xml tags - thinking through each criteria with a critical eye
Return your score (0-5) in <score> xml tags
Make sure to only respond with a score of 0 through 5 for your response in <score>, no other text, only the numerical score

"""
    # Constructing the user prompt containing the model name and summary generated by the respective model to be evaluated
    user_prompt = f"""
<model>
{model}
</model>

The model's output to be evaluated:
<models_response_to_be_evaluated>
{summary}
</models_response_to_be_evaluated>

"""
    # Acquiring an asynchronous client for invoking the evaluation model
    async with await get_bedrock_client() as client:
        # Executing the model asynchronously with the constructed prompts
        result = await model_execution(client, user_prompt, system_prompt)
    # Returning the result of model execution
    return result


def dynamic_grading_criteria(task):
    """
    Creates an evaluation framework and grading criteria for the task/prompt that the user inputted in the UI in the "Document Summary Task" TextBox

    This method dynamically generates the grading criteria, system prompt, and user
    prompt based on the source text, to allow for evaluation of different aspects
    of a summary beyond just accuracy.

    :param task: The task/prompt that the user inputted in the UI in the "Document Summary Task" TextBox
    :return: A tuple containing the score and evaluation summary
    """
    # Constructing the system prompt providing the task that was given to the models. Using Few shot of the other task types to dynamically create an evaluation criteria
    system_prompt = f"""
Your goal is to evaluate and compare an AI model's outputs/response
You will be evaluating a model based on how well it adhered to the provided task in the prompt (Task Adherence)
Only create your evaluation in regards to the tasks explicitly mentioned in the  <provided_prompt>; other criteria (Completeness, Accuracy, Logical Flow, Paragraph and Sentence Structure, Conciseness, Clarity, Tone, and Objectivity) will be evaluated in a different method.
Create an evaluation framework and a grading criteria for the provided task that will be used to assign a model a 0-5 score
Only provide the <evaluation_framework> and <evaluation_grading> in your response
If the provided task requires a specific number of sentences, paragraphs, or pages, make sure the evaluation criteria involves counting that accuracy
Use the examples provided as a guide to the format
Be fair but critical in your assessment 

This is the prompt/instructions that the models will be provided and that you will grade their adherence to
<provided_prompt>
{task}
</provided_prompt>

This is an example of a a evaluation criteria that was for the prompt "Summarize this document in 2 sentences. Return your summary in <summary></summary> xml tags. No other text"
Use this example framework as a guide for the creation of an evaluation criteria for Task Adherence to the <provided_prompt>:
<example_evaluation_criteria>

Task Adherence:
- Does the model's output contain a summary of the provided document?
- Is the summary contained within <summary></summary> XML tags?
- How many sentences does the summary consist of? Is it exactly 2? - pay extra attention to identifying and counting sentences accurately 
- Does the model's output contain any additional text outside of the summary within the XML tags?

</example_evaluation_criteria>

This is an example of a grading framework that was used for Tone Consistency. Use this example framework as a guide for the creation of a grading framework for Task Adherence to the <provided_prompt>:
<example_evaluation_grading>
5 - Excellent:
Tone Consistency: The summary exhibits exceptional consistency in tone with the source text. The overall level of formality, emotion, or attitude is maintained throughout, accurately reflecting the intended tone and mood of the original content. There are no shifts or inconsistencies in tone within the summary. If the source text has a neutral or objective tone, the summary maintains that impartial perspective. If the source text has a more subjective or emotional tone, the summary accurately captures and conveys that tone without being overly exaggerated or understated.

4 - Very Good:
Tone Consistency: The summary demonstrates very good consistency in tone with the source text. The overall level of formality, emotion, or attitude is largely maintained, with only minor deviations that do not significantly impact the intended tone and mood. There may be a few slight shifts in tone within the summary, but they are not out of place. If the source text has a neutral or objective tone, the summary generally maintains that impartial perspective. If the source text has a more subjective or emotional tone, the summary accurately reflects that tone, with occasional minor instances of exaggeration or understatement.

3 - Good:
Tone Consistency: The summary exhibits good consistency in tone with the source text. The overall level of formality, emotion, or attitude is reasonably maintained, though there may be a few noticeable deviations or inconsistencies in tone. There are some shifts in tone within the summary, but they do not significantly detract from the intended tone and mood. If the source text has a neutral or objective tone, the summary may occasionally veer into a more subjective perspective. If the source text has a more subjective or emotional tone, the summary may at times exaggerate or understate that tone.

2 - Fair:
Tone Consistency: The summary shows fair consistency in tone with the source text. The overall level of formality, emotion, or attitude is inconsistently maintained, with several noticeable deviations or inconsistencies in tone. There are frequent shifts in tone within the summary that may seem out of place or . If the source text has a neutral or objective tone, the summary often adopts a subjective perspective. If the source text has a more subjective or emotional tone, the summary frequently exaggerates or understates that tone.

1 - Poor:
Tone Consistency: The summary displays poor consistency in tone with the source text. The overall level of formality, emotion, or attitude is rarely maintained, with significant deviations or inconsistencies in tone throughout. There are numerous  shifts in tone within the summary that seem out of place or inappropriate. If the source text has a neutral or objective tone, the summary is predominantly subjective or opinionated. If the source text has a more subjective or emotional tone, the summary either greatly exaggerates or severely understates that tone.

0 - Unacceptable:
Tone Consistency: The summary lacks any discernible consistency in tone with the source text. The overall level of formality, emotion, or attitude bears no resemblance to the intended tone and mood of the original content. The tone within the summary is wildly inconsistent, with constant  shifts that make it impossible to establish a coherent tone. Regardless of whether the source text has a neutral or subjective tone, the summary fails to capture or convey any semblance of the appropriate tone.
</example_evaluation_grading>


Return your evaluation criteria for Task Adherence in <evaluation_criteria> xml tags, with no other text
Return your grading framework for Task Adherence in <evaluation_grading> xml tags. with no other text

"""
    # Constructing user prompt which provides the task
    user_prompt = f"""

This is the prompt/instructions that the models will be provided and that you will grade their adherence to
<provided_prompt>
{task}
</provided_prompt>
"""

    content = [{
        "type": "text",
        "text": user_prompt
    }]

    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10000,
        "temperature": 0,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }
    boto3.setup_default_session(profile_name=os.getenv("profile_name"))

    prompt = json.dumps(prompt)
    # get region name form env (or default to us-east-1 if it cant)
    try:
        region = os.getenv("region_name")
    except:
        region = "us-east-1"

    # create Bedrock client
    client = boto3.client('bedrock-runtime', region)
    # Invoking the Amazon Bedrock and the Claude 3 Sonnet model with the constructed prompt
    response = client.invoke_model(body=prompt, modelId="anthropic.claude-sonnet-4-6",
                                   accept="application/json", contentType="application/json")
    # Extracting and parsing the response from the AI model
    response_body = json.loads(response.get('body').read())
    response = response_body['content'][0]['text']

    eval_criteria = parse_xml(response, "evaluation_criteria").strip()
    eval_grading = parse_xml(response, "evaluation_grading").strip()

    # return the evaluation_criteria and evaluation_grading strings
    return eval_criteria, eval_grading


async def evaluate_model_output_orchestrator(source_text_data, model_name, model_summary, task, dynamic_evaluation_criteria, scale):
    """
    Orchestrates the evaluation of model output across multiple evaluation criteria and calculates the final evaluation score.

    :param source_text_data: The original source text data, extracted from the uploaded PDF.
    :param model_name: The name of the model being evaluated.
    :param model_summary: The summary generated by the respective model.
    :return: A tuple containing the final score and a summary of all the evaluation results.
    """
    # Evaluate the model output asynchronously across multiple evaluation criteria
    result = await asyncio.gather(eval_model_accuracy(model_name, model_summary, source_text_data),
                                  eval_model_completeness(model_name, model_summary, source_text_data),
                                  eval_model_flow(model_name, model_summary, source_text_data),
                                  eval_model_structure(model_name, model_summary, source_text_data),
                                  eval_model_conciseness(model_name, model_summary, source_text_data),
                                  eval_model_clarity(model_name, model_summary, source_text_data),
                                  eval_model_objectivity(model_name, model_summary, source_text_data),
                                  eval_model_tone(model_name, model_summary, source_text_data),
                                  eval_model_task(model_name, model_summary, source_text_data, task, dynamic_evaluation_criteria, scale))
    # Extract individual evaluation scores and summaries from the result
    model_accuracy_score, model_accuracy_summary = result[0]
    model_completeness_score, model_completeness_summary = result[1]
    model_flow_score, model_flow_summary = result[2]
    model_structure_score, model_structure_summary = result[3]
    model_conciseness_score, model_conciseness_summary = result[4]
    model_clarity_score, model_clarity_summary = result[5]
    model_objectivity_score, model_objectivity_summary = result[6]
    model_tone_score, model_tone_summary = result[7]
    model_task_score, model_task_summary = result[8]
    # Construct a dictionary containing individual evaluation scores
    final_score_rubric = {
        "model_name": model_name,
        "model_completeness_score": model_completeness_score,
        "model_accuracy_score": model_accuracy_score,
        "model_flow_score": model_flow_score,
        "model_structure_score": model_structure_score,
        "model_conciseness_score": model_conciseness_score,
        "model_clarity_score": model_clarity_score,
        "model_objectivity_score": model_objectivity_score,
        "model_tone_score": model_tone_score,
        "model_task_score": model_task_score
    }
    # Calculate the final score
    final_score = (int(model_completeness_score) + int(model_accuracy_score) + int(model_flow_score) + int(
        model_structure_score) +
                   int(model_conciseness_score) + int(model_clarity_score) + int(model_objectivity_score) + int(
                model_tone_score) + int(model_task_score)) / 9.0

    # Construct a summary of the evaluation results
    final_summary = f"""
Full Summary:
{model_summary}
---------------------------------------------------------------------

Model Completeness: 
Score: {model_completeness_score}
Summary: {model_completeness_summary}
---------------------------------------------------------------------

Model Accuracy: 
Score: {model_accuracy_score}
Summary: {model_accuracy_summary}
---------------------------------------------------------------------

Model Flow Summary: 
Score: {model_flow_score}
Summary: {model_flow_summary}
---------------------------------------------------------------------

Model Structure: 
Score: {model_structure_score}
Summary: {model_structure_summary}
---------------------------------------------------------------------

Model Conciseness: 
Score: {model_conciseness_score}
Summary: {model_conciseness_summary}
---------------------------------------------------------------------

Model Clarity Summary: 
Score: {model_clarity_score}
Summary: {model_clarity_summary}
---------------------------------------------------------------------

Model Objectivity:
Score: {model_objectivity_score}
Summary: {model_objectivity_summary}

---------------------------------------------------------------------

Model Tone:
Score: {model_tone_score}
Summary: {model_tone_summary}
---------------------------------------------------------------------

Model Task:
Score: {model_task_score}
Summary: {model_task_summary}
------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    # Return the final score, final summary, and final scoring rubric
    return final_score, final_summary, final_score_rubric

def evaluate_model_performance(csv_string, model_id="anthropic.claude-sonnet-4-6"):
    """
    Evaluates the performance of AI models based on provided CSV data.

    :param csv_string: A string containing CSV data with columns for 'Total Cost(1000)', 'Time Length', and 'Summary Score'.
    :param model_id: The ID of the model used for evaluation. Defaults to "anthropic.claude-3-sonnet-20240229-v1:0".
    :return: A string containing the analysis and findings of model performance based on the provided CSV data.
    """
    # Constructing a prompt for the Amazon Bedrock Claude 3 Sonnet model to analyze the provided CSV data
    prompt = f"""Human:

    Given the following CSV data on AI model performance:

    {csv_string}

    Please analyze the data and determine which model has the best performance in terms of cost efficiency and speed.
    
    'Total Cost(1000)' is the total cost in dollars for invoking the model 1000 times.
    'Time Length' is the time to invoke the model.
    'Summary Score' is the invoke response quality score.

    Criteria for evaluation:
    1) The model with the lowest 'Total Cost(1000)' is considered as least expensive. 
    2) The model with the highest 'Total Cost(1000)' is considered as most expensive.
    3) The model with the shortest 'Time Length' is considered as fastest.
    4) The model with the highest 'Summary Score' is considered as best summary result.
    4) The model with the lowest 'Summary Score' is considered as worse summary result.

    Summarize your findings on which model performs best on each criterion and overall. Identify the percent time and cost difference.
    
    Format in markdown.
    """
    # Constructing the prompt object for model execution
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }
    boto3.setup_default_session(profile_name=os.getenv("profile_name"))
    # Creating a boto3 client for interacting with the Bedrock Runtime service
    client = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv("region_name")
    )
    # Invoking the Amazon Bedrock and the Claude 3 Sonnet model with the constructed prompt
    response = client.invoke_model(
        modelId=model_id, body=json.dumps(prompt)
    )
    # Extracting and parsing the response from the AI model
    response_body = json.loads(response.get('body').read())
    response = response_body['content'][0]['text']
    # Returns a string containing the analysis and findings of model performance based on the provided CSV data.
    return response

def evaluate_rag_performance(csv_string, model_id="anthropic.claude-sonnet-4-6"):
    """
    Evaluates the performance of AI models based on provided CSV data.

    :param csv_string: A string containing CSV data with columns for 'Total Cost(1000)', 'Time Length', and 'Summary Score'.
    :param model_id: The ID of the model used for evaluation. Defaults to "anthropic.claude-3-sonnet-20240229-v1:0".
    :return: A string containing the analysis and findings of model performance based on the provided CSV data.
    """
    # Constructing a prompt for the Amazon Bedrock Claude 3 Sonnet model to analyze the provided CSV data
    prompt = f"""Human:

    Given the following CSV data on AI model performance:

    {csv_string}

    Please analyze the data and determine which model has the best performance in terms of cost efficiency and speed.
    
    'Total Cost(1000)' is the total cost in dollars for invoking the model 1000 times.
    'Time Length' is the time to invoke the model.
    'Score' is the invoke response quality score.

    Criteria for evaluation:
    1) The model with the lowest 'Total Embedding Cost(1000)' is considered as least expensive. 
    2) The model with the highest 'Total Embedding Cost(1000)' is considered as most expensive.
    3) The model with the shortest 'Time Length' is considered as fastest.
    4) The model with the highest 'Score' is considered as best answering result.
    4) The model with the lowest 'Score' is considered as worse answering result.

    Summarize your findings on which model performs best on each criterion and overall. Identify the percent time and cost difference.
    
    Format in markdown.
    """
    # Constructing the prompt object for model execution
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }
    boto3.setup_default_session(profile_name=os.getenv("profile_name"))
    # Creating a boto3 client for interacting with the Bedrock Runtime service
    client = boto3.client(
        service_name='bedrock-runtime',
        region_name=os.getenv("region_name")
    )
    # Invoking the Amazon Bedrock and the Claude 3 Sonnet model with the constructed prompt
    response = client.invoke_model(
        modelId=model_id, body=json.dumps(prompt)
    )
    # Extracting and parsing the response from the AI model
    response_body = json.loads(response.get('body').read())
    response = response_body['content'][0]['text']
    # Returns a string containing the analysis and findings of model performance based on the provided CSV data.
    return response



def evaluate_rag_output(result, knowledge_base, contexts):
    """
    Orchestrates the evaluation of model output across multiple evaluation criteria and calculates the final evaluation score.

    :param result: The golden output, extracted from the uploaded answer csv file.
    :param knowledge_base: The name of the knowledge base being evaluated.
    :param contexts: The extracted contexts from the knowledge base.
    :return: A tuple containing the final score and a summary of all the evaluation results.
    """
    # Construct a dictionary containing individual evaluation scores
    final_score_rubric = {
        "model_name": knowledge_base['name'],
        "faithfulness": result['faithfulness'],
        "answer_relevancy": result['answer_relevancy'],
        "context_precision": result['context_precision'],
        "context_recall": result['context_recall'],
        "context_entity_recall": result['context_entity_recall'],
        "answer_similarity": result['answer_similarity'],
        "answer_correctness": result['answer_correctness'],
        "harmfulness": result['harmfulness'],
        "maliciousness": result['maliciousness'],
        "coherence": result['coherence'],
        "correctness": result['correctness'],
        "conciseness": result['conciseness']

    }
    # Calculate the final score
    final_score = (result['faithfulness'] + result['answer_relevancy'] + result['context_precision'] + 
        result['context_recall'] + result['context_entity_recall'] + result['answer_similarity'] + result['answer_correctness']
        + result['coherence'] + result['correctness'] + result['conciseness']) / 10.0
    final_score -= ((result['maliciousness'] + result['harmfulness']) / 2.0)

    # Construct a summary of the evaluation results
    final_summary = f"""
Full Output:
{contexts}
---------------------------------------------------------------------

Knowledge Base Faithfulness: 
Score: {result['faithfulness']}
---------------------------------------------------------------------

Knowledge Base Answer Relevancy: 
Score: {result['answer_relevancy']}
---------------------------------------------------------------------

Knowledge Base Context Precision: 
Score: {result['context_precision']}
---------------------------------------------------------------------

Knowledge Base Context Recall: 
Score: {result['context_recall']}
---------------------------------------------------------------------

Knowledge Base Context Entity Recall: 
Score: {result['context_entity_recall']}
---------------------------------------------------------------------

Knowledge Base Answer Similarity: 
Score: {result['answer_similarity']}
---------------------------------------------------------------------

Knowledge Base Answer Correctness:
Score: {result['answer_correctness']}

---------------------------------------------------------------------

Knowledge Base Harmfulness:
Score: {result['harmfulness']}
---------------------------------------------------------------------

Knowledge Base Maliciousness:
Score: {result['maliciousness']}
---------------------------------------------------------------------

Knowledge Base Coherence:
Score: {result['coherence']}
---------------------------------------------------------------------

Knowledge Base Correctness:
Score: {result['correctness']}
---------------------------------------------------------------------

Knowledge Base Conciseness:
Score: {result['conciseness']}
------------------------------------------------------------------------------------------------------------------------------------------------------------
    """
    # Return the final score, final summary, and final scoring rubric
    return final_score, final_summary, final_score_rubric
