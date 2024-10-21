import os
from langchain.llms.bedrock import Bedrock
from langchain.chains import ConversationChain
from langchain.agents import load_tools,initialize_agent, Tool, load_tools
from langchain_community.tools.google_jobs import GoogleJobsQueryRun
from langchain_community.utilities.google_jobs import GoogleJobsAPIWrapper
from langchain.agents import initialize_agent, Tool, AgentType

from dotenv import load_dotenv
load_dotenv()

def init_llm():
        
    model_parameter = {"temperature": 0, "top_p": 0.5, "max_tokens_to_sample": 2000}
    llm = Bedrock(
        credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"), 
        region_name=os.environ.get("BWB_REGION_NAME"), 
        endpoint_url=os.environ.get("BWB_ENDPOINT_URL"), 
        model_id="anthropic.claude-instant-v1", 
        model_kwargs=model_parameter,
        ) 
    
    return llm

def get_llm(streaming_callback):
        
    model_parameter = {"temperature": 1, "top_p": 0.5, "max_tokens_to_sample": 2000}
    llm = Bedrock(
        credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"), 
        region_name=os.environ.get("BWB_REGION_NAME"), 
        endpoint_url=os.environ.get("BWB_ENDPOINT_URL"), 
        model_id="anthropic.claude-instant-v1", 
        model_kwargs=model_parameter,
        streaming=True,
        callbacks=[streaming_callback]
        ) 
    
    return llm

def get_rag_chat_response(input_text, streaming_callback): 
    llm = get_llm(streaming_callback)
    return llm.invoke(input=input_text)

def rewrite_resume(input_text, streaming_callback): 
    model_parameter = {"temperature": 1, "top_p": 1, "max_tokens_to_sample": 2000}
    llm = Bedrock(
        credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"), 
        region_name=os.environ.get("BWB_REGION_NAME"), 
        endpoint_url=os.environ.get("BWB_ENDPOINT_URL"), 
        model_id="anthropic.claude-instant-v1", 
        model_kwargs=model_parameter,
        callbacks=[streaming_callback]

        ) 
    prompt = """Your name is Head Hunter. You are the best recruitment consultant expert, you will rewrite the input resume in better format
    . You only need to rewrite content and do not give instruction: 
        \n\nHuman: here is the resume content
        <text>""" + str(input_text) + """</text>
    \n\nAssistant: """
    return llm.invoke(input=prompt)


def summary_resume_stream(input_text, streaming_callback): 
    llm = get_llm(streaming_callback)
    prompt = """You are the best recruitment consultant expert, you will scan the resume and output concide content for the following informantion: 
        Contact, Experience, Skills,Certificates and suggested jobs based on the resume in a bulleted list in <response> tag.
        Output all content same as input language with the following format
         Contact:
         Experience:
         Skills:
         Certificates:
         Suggested jobs:
        \n\nHuman: here is the resume content
        <text>""" + str(input_text) + """</text>
    \n\nAssistant: """

    return llm.invoke(prompt)


def suggested_jobs(input_text): 
    llm = init_llm()
    prompt = """You are the best recruitment consultant expert, you will scan the resume and output concise content for the following informantion: 
            suggest jobs based on the resume.
        Put your response in <response></response> tags
        \n\nHuman: here is the resume content
        <text>""" + input_text + """</text>
    \n\nAssistant: """
    print(input_text)
    return llm.invoke(prompt)

    
def get_jobs(jobs):
    tool = GoogleJobsQueryRun(api_wrapper=GoogleJobsAPIWrapper())  
    res =  tool.run(jobs)
    print(res)
    return res

def search_jobs(input_text, st_callback):
    tools=[
        Tool(
            name="search jobs",
            func=get_jobs,
            description="Use this to search jobs"
        ),
    ]
    agent = initialize_agent(tools=tools,llm=init_llm(),agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    
    prompt="""\n\nHuman: You are a jobs advisor. Give a job summary with the format in a bulleted list
    <format>
       - Job Title
       - Salary
       - Location
       - Company name
       - Job description
    </format>

<steps>
    1) Use "search jobs" tool to search jobs. Output- List of Jobs
    2) Provide summary for the job with Job Title, Salary, Location, Company name, Job description
</steps>
Use the following format:
Question: the input resume you must scan to suggest jobs
Thought: you should always think about what to do, Also try to follow All steps mentioned above
Action: the action to take, should be one of [search jobs]
Action Input: the input to the action
Observation: the result of the action
Thought: I now know the final answer
Final Answer: the final answer to the original input question
 {input}

\n\nAssistant:
{agent_scratchpad}

"""
    agent.agent.llm_chain.prompt.template=prompt
    response = agent({
            "input": str(input_text),
            "output":"output",
            "chat_history": [],
         },
    callbacks=[st_callback])
    return response

def initializeAgent():
    tools=[
    Tool(
        name="get suggested jobs",
        func=suggested_jobs,
        description="use this tool get suggested jobs for resume")
]
    agent=initialize_agent(
    llm=init_llm(),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    tools=tools,
    verbose=True,
    max_iteration=1,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
    output_key="output",
)
    prompt="""You are a jobs advisor. Give jobs recommendations for given resume based on following instructions. 
<instructions>
    Answer the following questions as best as you can. You have access to the following tools:
      get suggested jobs: use this tool get suggested jobs for a input resume.
</instructions>

<steps>
    1) Use "get suggested jobs" tool get suggested jobs for a input resume. Output- job title
</steps>

Use the following format:
Question: the input resume you must scan to suggest jobs
Thought: you should always think about what to do, Also try to follow steps mentioned above
Action: the action to take, should be one of [get suggested jobs]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

\n\nHuman:
Here is the user question: {input}

\n\nAssistant: 
{agent_scratchpad}

"""
    agent.agent.llm_chain.prompt.template=prompt
    return agent
    
def query_resume(question, resume, streaming_callback): 
    llm = get_llm(streaming_callback)
    prompt = """Human: here is the resume content:
        <text>""" + str(resume) + """</text>
        Question: """ + question + """ 
    \n\nAssistant: """

    return llm.invoke(prompt)