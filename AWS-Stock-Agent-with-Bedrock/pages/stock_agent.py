import streamlit as st
import boto3
from langchain_aws import ChatBedrock

import json
from anthropic import Anthropic
from datetime import date
from datetime import datetime, timedelta
import pandas as pd
import os
from vnstock3 import Vnstock
from bs4 import BeautifulSoup
import re
import requests
from langchain.agents import initialize_agent, Tool
from langchain.callbacks import StreamlitCallbackHandler
import base

# Setting page title and header

st.set_page_config(page_title="Trợ lý chứng khoán", page_icon="img/favicon.ico", layout="wide")
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

st.title('Trợ lý chứng khoán')

base.init_home_state("RoboStock - Your 24/7 AI financial companion")
base.init_slidebar()
base.init_dialog()
base.init_animation()

anthropic = Anthropic()
knowledge_base_id=("EWVHJIY9AS")

modelId = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    
def get_llm():      
    # Configure the model to use
    model_id = modelId
    model_kwargs = {
        "max_tokens": 2048,
        "temperature": 0.2,
        "top_k": 250,
        "top_p": 1,
        #"stop_sequences": ["\n\nHuman"],
    }
    bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name=os.environ.get("BWB_REGION_NAME"))
    llm = ChatBedrock(
        client=bedrock_runtime,
        model_id=model_id,
        model_kwargs=model_kwargs,
        streaming = True
    )
    return llm

# Function to parse and validate response
def parse_response(content):
  try:
      parsed_data = json.loads(content)
      company_name = parsed_data[0].get('company_name', 'Unknown')
      company_ticker = parsed_data[0].get('company_ticker', 'Unknown')
      return company_name, company_ticker
  except (json.JSONDecodeError, KeyError):
      return 'Unknown', 'Unknown'

# Function to invoke Bedrock model
def invoke_bedrock_model(prompt,max_tokens=2000):
    bedrock_runtime = boto3.client('bedrock-runtime')
    request_body = {
      "anthropic_version": "bedrock-2023-05-31",
      "max_tokens": max_tokens,
      "messages": [
          {"role": "user", "content": prompt}
      ],
      "temperature": 0,
      "top_p": 1,
    }
  
    response = bedrock_runtime.invoke_model(
      modelId=modelId,
      contentType="application/json",
      accept="application/json",
      body=json.dumps(request_body)
    )
    response_body = json.loads(response['body'].read().decode())
    return response_body['content'][0]['text']

def get_stock_ticker(question):
    # load company name & company tiker
    with open('data-02.csv', 'r') as file:
        company_data = file.read()        

    prompt = f"""You are an AI assistant designed to extract company ticker symbols and company names from user input. 
            You have access to a comprehensive list of Vietnamese company tickers and their corresponding company names.
            Instructions:
            1. Carefully analyze the user's input.
            2. Identify any mentions of company names or ticker symbols.
            3. Cross-reference the identified information with your list of company tickers and names.
            4. If a match is found, extract the company ticker and full company name.
            5. If multiple companies are mentioned, focus on the most prominent or relevant one.
            6. If no clear match is found, use your best judgment to infer the company based on context.
            7. Format your response as a JSON object with the following keys:
                - company_ticker: The ticker symbol of the identified company (in uppercase)
                - company_name: The full name of the identified company
            Rules:
            - Always provide a response, even if you're not 100% certain.
            - If you cannot identify a company, use "UNKNOWN" for both the ticker and name.
            - Ensure the company_ticker is in uppercase letters.
            - Provide the full, official company name for company_name.

            Example user inputs and expected outputs:

            Input: "Đánh gía cổ phiếu HPG?"
            Output:
            {{
            "company_ticker": "HPG",
            "company_name": "Công ty Cổ phần Tập đoàn Hòa Phát"
            }}

            Input: "Định giá cổ phiếu ngân hàng sài gòn thương tín"
            Output:
            {{
            "company_ticker": "STB",
            "company_name": "Ngân hàng Thương mại Cổ phần Sài Gòn Thương Tín"
            }}

            Input: "Phân tích tình hình tài chính công ty đầu tư xây dựng Kiên Giang"
            Output:
            {{
            "company_ticker": "CKG",
            "company_name": "Công ty Cổ phần Tập đoàn Tư vấn Đầu tư Xây dựng Kiên Giang"
            }}

            Input: "Đánh giá thị trường hiện tại?"
            Output:
            {{
            "company_ticker": "UNKNOWN",
            "company_name": "UNKNOWN"
            }}

            Remember to always format your response as a JSON object with the specified keys, regardless of the input or your level of certainty.
            Additional Guidelines:
            - Focus only on Vietnamese companies in the provided list
            - Use the exact company name and ticker from the list - do not modify or paraphrase them
            <context>
            Vietnamese company list: {json.dumps(company_data)}
            </context>

            Input: {question}

            Output: JSON array of objects with keys 'company_name' and 'company_ticker'.
            Respond only with the JSON array. Do not include any explanations or additional text.
        """
    initial_response = invoke_bedrock_model(prompt)
    company_name, company_ticker = parse_response(initial_response)    

    with open("company.json", 'w') as file:
        file.write(str(json.dumps({'company_name': company_name, 'company_ticker': company_ticker})))

    return company_name, company_ticker

# get stock history of the company in 3 years
def get_stock_price(ticker, history=1000):
    with open("company.json", 'a') as file:
        file.write(f'\nget stock price for ticker: {ticker}')
    today = date.today()
    start_date = today - timedelta(days=history)
    stock = Vnstock().stock(symbol=ticker.strip(), source='TCBS')
    data = stock.quote.history(start=start_date.strftime('%Y-%m-%d'),end=today.strftime('%Y-%m-%d'))
    return data

# Function to safely get data and handle exceptions
def safe_get_data(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"Error getting data: {e}")
        return pd.DataFrame()

# Function to get financial data
def get_financial_data(ticker):
    # Create a stock object for financial data
    ticker = ticker.strip().upper()
    stock_finance = Vnstock().stock(symbol=ticker, source='VCI')
    
    # Create a dictionary to store all dataframes
    company_data = {
        'Balance Sheet Yearly': safe_get_data(stock_finance.finance.balance_sheet, period='year', lang='en'),
        'Balance Sheet Quarterly': safe_get_data(stock_finance.finance.balance_sheet, period='quarter', lang='en'),
        'Income Statement Yearly': safe_get_data(stock_finance.finance.income_statement, period='year', lang='en'),
        'Income Statement Quarterly': safe_get_data(stock_finance.finance.income_statement, period='quarter', lang='en'),
        'Cash Flow Yearly': safe_get_data(stock_finance.finance.cash_flow, period='year', lang='en'),
        'Cash Flow Quarterly': safe_get_data(stock_finance.finance.cash_flow, period='quarter', lang='en'),
        'Financial Ratios Yearly': safe_get_data(stock_finance.finance.ratio, period='year', lang='en'),
        'Financial Ratios Quarterly': safe_get_data(stock_finance.finance.ratio, period='quarter', lang='en'),
    }
    return company_data

def get_financial_statements(ticker):
    stock = Vnstock().stock(symbol=ticker.upper(), source='VCI')
    data = stock.finance.balance_sheet(period='year', lang='en')
    return data

# Script to scrap top5 googgle news for given company name
def google_query(search_term):
    if "news" not in search_term:
        search_term=search_term+" stock news"
    url=f"https://www.google.com/search?q={search_term}+tin+tức&hl=vi&tbm=nws"
    url=re.sub(r"\s","+",url)
    return url


def get_recent_stock_news(ticker):
    # get company name from ticker
    ticker = ticker.strip().upper()
    articles = fetch_news(ticker)
    content = []
    for article in articles:
        content.append({'summary': article['summary'], 'content':fetch_article_content(article['link'])})
    return content

#search for news and scrap 5 recent news
def fetch_news(query):
    base_url = "https://cafef.vn/tim-kiem.chn"
    # Configure the request parameters
    params = {'keywords': query}
    # Make the request
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Ensure the request was successful
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the container with the news items
    news_container = soup.find('div', class_='list-section list-event')
    news_items = news_container.find_all('div', class_='item')
    # List to hold news data
    articles = []
    # Loop through each news item
    for item in news_items:
        title_element = item.find('h3', class_='titlehidden').find('a')
        title = title_element.text.strip()
        link = 'https://cafef.vn' + title_element['href']
        summary = item.find('p', class_='sapo').text.strip() if item.find('p', class_='sapo') else 'No summary available'
        # Append news info to the list
        articles.append({'link': link, 'summary': summary})
    return articles[:5]

# fetch article content from link
def fetch_article_content(url):
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the specific container holding the main content
    content_div = soup.find('div', class_='detail-content afcbc-body')
    if not content_div:
        return "Content not found"
    # Extract all paragraph texts within the container
    paragraphs = content_div.find_all('p')
    main_content = "\n".join(p.text.strip() for p in paragraphs)
    return main_content

def initializeAgent():
    
    zero_shot_agent = initialize_agent(
        llm=get_llm(),
        agent="zero-shot-react-description",
        tools=tools,
        verbose=True,
        max_iteration=4,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        output_key="output",
    )
    
    CURRENT_DATE = datetime.today().strftime("%Y-%m-%d")
    prompt = f"""
        You are CRobo Advisor, an AI-powered stock analysis and investment assistant. Y
        our goal is to provide expert financial analysis and actionable insights in Vietnamese. Follow these guidelines:

        1. Expertise: Deliver in-depth financial market analysis, utilize technical analysis tools and indicators, 
        and conduct quantitative analysis (e.g., DCF, P/E ratio, ROE).

        2. Data Presentation: Present numerical data and statistics clearly, using Markdown for clarity (e.g., **bold** for key points)

        3. Communication: Explain complex concepts clearly, translate technical terms into Vietnamese, 
        and tailor responses to the user's level of expertise.

        4. Recommendations: Provide comprehensive lists with supporting data, 
        explain why assets/strategies meet criteria, and include potential risks and limitations.

        5. Market Insights: Analyze market structures and trading dynamics, use up-to-date market data, 
        and focus on key insights and trends.

        6. Transparency: Be clear about any uncertainties or limitations in your analysis.

        7. Response Format: Interpret data, don't just repeat it. Balance comprehensive analysis with actionable information.

        8. Time Awareness: Always consider the current date: {CURRENT_DATE}

        Available Tools (these are external tools you can call):
        - get company ticker: Extract company name and ticker
        - get stock data: Retrieve stock information
        - get recent stock news: Fetch recent stock news
        - get financial data: Obtain company financial data

        Analysis Steps:
        1. Use "get company ticker" to identify company and ticker. Once you have this information, immediately proceed to step 2.
        2. Use "get stock data" with the exact ticker obtained in step 1. After getting this data, move to step 3.
        3. Use "get recent stock news" with the exact ticker from step 1. After obtaining news, proceed to step 4.
        4. Use "get financial data" with the exact ticker from step 1. 
        5. After completing steps 1-4, analyze all collected information to answer the user's query.

        IMPORTANT: Follow this exact format for your response, ensuring you progress through all steps:

        Question: [User's input question]
        Thought: [Your reasoning about the current step, including what you've learned so far and what you need to do next]
        Action: action to take, should be one of [get company ticker, get stock data, get recent stock news, get financial data]
        Action Input: [Input for the chosen action]
        Observation: [Result of the action]
        Thought: [Analyze the result and determine the next step. If you have completed a step, explicitly state that you're moving to the next one.]
        ... (Repeat Thought/Action/Action Input/Observation for each step, ensuring you progress through all four data gathering steps before final analysis)
        Thought: I have gathered all necessary information and can now provide a final answer
        Final Answer: [Your comprehensive response in Vietnamese]

        Remember:
        - You must progress through all four data gathering steps before providing a final answer.
        - After getting the ticker, always verify it by explicitly stating: "Mã cổ phiếu được xác định: [TICKER]"
        - Ensure you're passing the ticker exactly as received, without any modifications.
        - If you encounter an error, report it precisely and attempt to proceed with the next step.
        - Your final answer must synthesize information from all steps and be in Vietnamese.
        - Prioritize accuracy and completeness over speed.
        
        Begin!
        Question: {{input}}
        Thought: {{agent_scratchpad}}
""" 

    zero_shot_agent.agent.llm_chain.prompt.template=prompt
    
    return zero_shot_agent

tools = [
    Tool(
        name="get company ticker",
        func=get_stock_ticker,
        description="Extract company name and ticker from the user's question. Input: user question. Output: company name and ticker."
    ),
    Tool(
        name="get stock data",
        func=get_stock_price,
        description="Retrieve historical share price data for stock analysis. Input: EXACT company ticker. Output: historic share price data."
    ),
    Tool(
        name="get recent stock news",
        func=get_recent_stock_news,
        description="Fetch recent news about the stock. Input: EXACT company ticker. Output: list ofrecent news articles in json format with keys is summary,and content."
    ),
    Tool(
        name="get financial data",
        func=get_financial_data,
        description="""Retrieve comprehensive financial data for a company. Input: EXACT company ticker. 
                Output: A dictionary containing the following financial reports:
                1. Balance Sheet (Yearly and Quarterly)
                2. Income Statement (Yearly and Quarterly)
                3. Cash Flow Statement (Yearly and Quarterly)
                4. Financial Ratios (Yearly and Quarterly)
                Each report is provided in English and includes both annual and quarterly data.
                Use this data to conduct in-depth financial analysis, assess the company's financial health, 
                track performance trends, and evaluate key financial metrics over time.
        """
    )
]

zero_shot_agent = initializeAgent()

if 'chat_history' not in st.session_state: 
    st.session_state.chat_history = [] 

def generate_response(prompt, st_callback):
    
    response = zero_shot_agent(
        {
            "input": prompt,
            "chat_history": st.session_state.chat_history,
         },
         callbacks=[st_callback]
    )
    return response.get('body'), prompt

# Containers
# response_container = st.container()
# container = st.container()

# with container:
#     with st.form(key='my_form', clear_on_submit=True):
#         user_input = st.text_area("You:", key='input', height=100)
#         submit_button = st.form_submit_button(label='Send')

#     if submit_button and user_input:
#         st_callback = StreamlitCallbackHandler(st.container())
#         response_stream, query = generate_response(user_input,st_callback)

if prompt := st.chat_input():
    st.session_state.show_animation = False
    st.session_state.messages.append({"role": "user", "content": prompt})
    base.right_message(st, prompt)

if st.session_state.messages[-1]["role"] != "assistant":
    st.session_state.show_animation = False
    if prompt:
        with st.chat_message(
            "assistant",
            avatar="img/fcj.png",
        ) as chat:
            st_callback = StreamlitCallbackHandler(st)
            response, query = generate_response(prompt, st_callback)
            print(query)
            # full_response = st.write_stream(query)
            message = {"role": "assistant", "content": "Question: " + query}
            st.session_state.messages.append(message)
     
