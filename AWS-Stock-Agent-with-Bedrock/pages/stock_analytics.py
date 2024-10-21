import pandas as pd
import yfinance as yf
import streamlit as st
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import boto3, json
import pandas_datareader as pdr
import base

st.set_page_config(page_title="Phân tích kỹ thuật cổ phiếu", page_icon="img/favicon.ico", layout="wide")
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

st.title('Phân tích kỹ thuật cổ phiếu')

base.init_slidebar()
base.init_animation()

snp500 = pd.read_csv("data-01.csv")
symbols = snp500['Symbol'].sort_values().tolist()    

ticker = st.sidebar.selectbox('Chọn mã chứng khoán', symbols)
infoType = st.sidebar.radio("Chọn kiểu phân tích", ('PTKT', 'PTCB'))

# price
def get_stock_price(ticker, history=500):
    today = dt.datetime.today()
    start_date = today - dt.timedelta(days=history)
    df_price = pdr.get_data_yahoo(ticker, start=start_date, end=today)
    #print(df_price)
    return df_price

def plot_stock_price(ticker, history=500):
    df_price = get_stock_price(ticker, history)
    # Create the price chart
    fig = go.Figure(df_price=[go.Scatter(x=df['Date'], y=df_price['Adj Close'], mode='lines', name='Adjusted Close')])
    fig.update_layout(
        title=f'Stock Price for {ticker}',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        yaxis_tickprefix='$'
    )
    fig.update_yaxes(tickprefix="$")
    st.plotly_chart(fig, use_container_width=True)

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

    body = json.dumps(prompt_config)

    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
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

def forecast_price(question, docs): 
    prompt = """Human: here is the data price:
        <text>""" + str(docs) + """</text>
        Question: """ + question + """ 
    \n\nAssistant: """
    return call_claude_sonet_stream(prompt)

# stock = yf.Ticker(ticker)
if(infoType == 'PTCB'):
    stock = yf.Ticker(ticker)
    info = stock.info

    # Extract and print specific fundamental information
    # print(f"Company Name: {info.get('longName')}")
    # print(f"Market Cap: {info.get('marketCap')}")
    # print(f"Price-to-Earnings Ratio (P/E): {info.get('forwardPE')}")
    # print(f"Earnings Per Share (EPS): {info.get('forwardEps')}")
    # print(f"Sector: {info.get('sector')}")
    # print(f"Industry: {info.get('industry')}")
    # print(f"Website: {info.get('website')}")

    # translate summary to Vietnamese
    prompt = """Human: Summarize this content into no more than 100 words and translate into Vietnamese, return only vietnamese text of the question:
        Question: """ + str(info.get('longBusinessSummary', '')) + """
        
        \n\nAssistant: """
    response = call_claude_sonet_stream(prompt)
    
    if info:
        st.subheader('Thông tin công ty')
        st.subheader(info.get('name', '')) 
        st.markdown('**Lĩnh vực**: ' + info.get('sector', ''))
        st.markdown('**Ngành**: ' + info.get('industry', ''))
        st.markdown('**Liên hệ**: ' + info.get('phone', ''))
        st.markdown('**Địa chỉ**: ' + info.get('address1', '') + ', ' + info.get('city', '') + ', ' + info.get('zip', '') + ', '  +  info.get('country', ''))
        st.markdown('**Website**: ' + info.get('website', ''))
        st.markdown('**Tóm tắt**')
        #st.info(info.get('longBusinessSummary', ''))    
        st.write_stream(response)

        fundInfo = {
            'Giá trị doanh nghiệp (USD)': info.get('enterpriseValue', ''),
            'Tỷ lệ giá trị doanh nghiệp trên doanh thu': info.get('enterpriseToRevenue', ''),
            'Tỷ lệ giá trị doanh nghiệp trên EBITDA': info.get('enterpriseToEbitda', ''),
            'Thu nhập ròng (USD)': info.get('netIncomeToCommon', ''),
            'Tỷ suất lợi nhuận': info.get('profitMargins', ''),
            'Tỷ số P/E dự phóng': info.get('forwardPE', ''),
            'Tỷ số PEG': info.get('pegRatio', ''),
            'Tỷ số giá trên giá trị sổ sách': info.get('priceToBook', ''),
            'EPS dự phóng (USD)': info.get('forwardEps', ''),
            'Hệ số Beta': info.get('beta', ''),
            'Giá trị sổ sách (USD)': info.get('bookValue', ''),
            'Tỷ lệ cổ tức (%)': info.get('dividendRate', ''),
            'Lợi suất cổ tức (%)': info.get('dividendYield', ''),
            'Lợi suất cổ tức trung bình 5 năm (%)': info.get('fiveYearAvgDividendYield', ''),
            'Tỷ lệ chi trả cổ tức': info.get('payoutRatio', '')
        }
        
        fundDF = pd.DataFrame.from_dict(fundInfo, orient='index')
        fundDF = fundDF.rename(columns={0: 'Value'})
        st.subheader('Thông tin cơ bản')
        st.table(fundDF)

        st.subheader('Thông tin chung về cổ phiếu')
        st.markdown('**Thị trường**: ' + info.get('market', ''))
        st.markdown('**Sàn giao dịch**: ' + info.get('exchange', ''))
        st.markdown('**Loại báo giá**: ' + info.get('quoteType', ''))        
        start = dt.datetime.today()-dt.timedelta(365)
        end = dt.datetime.today()
        df = yf.download(ticker,start,end)
        df = df.reset_index()
        fig = go.Figure(
                data=go.Scatter(x=df['Date'], y=df['Adj Close'])
        )
        
        fig.update_layout(
            title={
                'text': "Giá trị cổ phiếu trong vòng 2 năm",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'})
        st.plotly_chart(fig, use_container_width=True)
    
        marketInfo = {
        "Khối lượng giao dịch": info.get('volume', ''),
        "Khối lượng giao dịch trung bình": info.get('averageVolume', ''),
        "Vốn hóa thị trường": info.get('marketCap', ''),
        "Số cổ phiếu lưu hành tự do": info.get('floatShares', ''),
        "Giá thị trường thông thường (USD)": info.get('regularMarketPrice', ''),
        'Khối lượng đặt mua': info.get('bidSize', ''),
        'Khối lượng đặt bán': info.get('askSize', ''),
        "Số cổ phiếu bán khống": info.get('sharesShort', ''),
        'Tỷ lệ bán khống': info.get('shortRatio', ''),
        'Tổng số cổ phiếu đang lưu hành': info.get('sharesOutstanding', '')
        }      
        marketDF = pd.DataFrame(data=marketInfo, index=[0])
        st.table(marketDF)
else:
    def calcMovingAverage(data, size):
        df = data.copy()
        df['sma'] = df['Adj Close'].rolling(size).mean()
        df['ema'] = df['Adj Close'].ewm(span=size, min_periods=size).mean()
        df.dropna(inplace=True)
        return df
    
    def calc_macd(data):
        df = data.copy()
        df['ema12'] = df['Adj Close'].ewm(span=12, min_periods=12).mean()
        df['ema26'] = df['Adj Close'].ewm(span=26, min_periods=26).mean()
        df['macd'] = df['ema12'] - df['ema26']
        df['signal'] = df['macd'].ewm(span=9, min_periods=9).mean()
        df.dropna(inplace=True)
        return df

    def calcBollinger(data, size):
        df = data.copy()
        df["sma"] = df['Adj Close'].rolling(size).mean()
        df["bolu"] = df["sma"] + df['Adj Close'].rolling(size).std(ddof=0) 
        df["bold"] = df["sma"] - df['Adj Close'].rolling(size).std(ddof=0) 
        df["width"] = df["bolu"] - df["bold"]
        df.dropna(inplace=True)
        return df
    
    st.subheader('Moving Average')
    
    coMA1, coMA2 = st.columns(2)
    
    with coMA1:
        numYearMA = st.number_input('Insert period (Year): ', min_value=1, max_value=10, value=2, key=0)    
    
    with coMA2:
        windowSizeMA = st.number_input('Window Size (Day): ', min_value=5, max_value=500, value=20, key=1)  
        
    start = dt.datetime.today()-dt.timedelta(numYearMA * 365)
    end = dt.datetime.today()
    dataMA = yf.download(ticker,start,end)
    df_ma = calcMovingAverage(dataMA, windowSizeMA)
    df_ma = df_ma.reset_index()
        
    figMA = go.Figure()
    
    figMA.add_trace(
            go.Scatter(
                    x = df_ma['Date'],
                    y = df_ma['Adj Close'],
                    name = "Prices Over Last " + str(numYearMA) + " Year(s)"
                )
        )
    
    figMA.add_trace(
                go.Scatter(
                        x = df_ma['Date'],
                        y = df_ma['sma'],
                        name = "SMA" + str(windowSizeMA) + " Over Last " + str(numYearMA) + " Year(s)"
                    )
            )
    
    figMA.add_trace(
                go.Scatter(
                        x = df_ma['Date'],
                        y = df_ma['ema'],
                        name = "EMA" + str(windowSizeMA) + " Over Last " + str(numYearMA) + " Year(s)"
                    )
            )
    
    figMA.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    
    figMA.update_layout(legend_title_text='Trend')
    figMA.update_yaxes(tickprefix="$")
    
    st.plotly_chart(figMA, use_container_width=True)  
    df_ma_file = df_ma.to_csv().encode('utf-8')
    #print(df_ma_file)
    st.subheader('Moving Average Convergence Divergence (MACD)')
    numYearMACD = st.number_input('Insert period (Year): ', min_value=1, max_value=10, value=2, key=2) 
    
    startMACD = dt.datetime.today()-dt.timedelta(numYearMACD * 365)
    endMACD = dt.datetime.today()
    dataMACD = yf.download(ticker,startMACD,endMACD)
    df_macd = calc_macd(dataMACD)
    df_macd = df_macd.reset_index()
   
    figMACD = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.01)
    # print(df_macd)
    figMACD.add_trace(
            go.Scatter(
                    x = df_macd['Date'],
                    y = df_macd['Adj Close'],
                    name = "Prices Over Last " + str(numYearMACD) + " Year(s)"
                ),
            row=1, col=1
        )
    
    figMACD.add_trace(
            go.Scatter(
                    x = df_macd['Date'],
                    y = df_macd['ema12'],
                    name = "EMA 12 Over Last " + str(numYearMACD) + " Year(s)"
                ),
            row=1, col=1
        )
    
    figMACD.add_trace(
            go.Scatter(
                    x = df_macd['Date'],
                    y = df_macd['ema26'],
                    name = "EMA 26 Over Last " + str(numYearMACD) + " Year(s)"
                ),
            row=1, col=1
        )
    
    figMACD.add_trace(
            go.Scatter(
                    x = df_macd['Date'],
                    y = df_macd['macd'],
                    name = "MACD Line"
                ),
            row=2, col=1
        )
    
    figMACD.add_trace(
            go.Scatter(
                    x = df_macd['Date'],
                    y = df_macd['signal'],
                    name = "Signal Line"
                ),
            row=2, col=1
        )
    
    figMACD.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="left",
        x=0
    ))
    
    figMACD.update_yaxes(tickprefix="$")
    st.plotly_chart(figMACD, use_container_width=True)
    
    st.subheader('Bollinger Band')
    coBoll1, coBoll2 = st.columns(2)
    with coBoll1:
        numYearBoll = st.number_input('Insert period (Year): ', min_value=1, max_value=10, value=2, key=6) 
        
    with coBoll2:
        windowSizeBoll = st.number_input('Window Size (Day): ', min_value=5, max_value=500, value=20, key=7)
    
    startBoll= dt.datetime.today()-dt.timedelta(numYearBoll * 365)
    endBoll = dt.datetime.today()
    dataBoll = yf.download(ticker,startBoll,endBoll)
    df_boll = calcBollinger(dataBoll, windowSizeBoll)
    df_boll = df_boll.reset_index()
    figBoll = go.Figure()
    figBoll.add_trace(
            go.Scatter(
                    x = df_boll['Date'],
                    y = df_boll['bolu'],
                    name = "Upper Band"
                )
        )
    
    figBoll.add_trace(
                go.Scatter(
                        x = df_boll['Date'],
                        y = df_boll['sma'],
                        name = "SMA" + str(windowSizeBoll) + " Over Last " + str(numYearBoll) + " Year(s)"
                    )
            )
    
    
    figBoll.add_trace(
                go.Scatter(
                        x = df_boll['Date'],
                        y = df_boll['bold'],
                        name = "Lower Band"
                    )
            )
    
    figBoll.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1,
        xanchor="left",
        x=0
    ))
    
    figBoll.update_yaxes(tickprefix="$")
    st.plotly_chart(figBoll, use_container_width=True)
    
    # Forecast stock
    st.title('Dự đoán theo chỉ số kỹ thuật')
    st.write("---")
    st.subheader('Dự đoán với chỉ số MACD')
    response = forecast_price(question="Dựa vào các chỉ số trên đưa ra phân tích giá chứng khoán trong thời gian tới,thời điểm, đưa ra giá mua vào và bán ra cổ phiếu cụ thể, giá cổ phiếu là VND", docs = df_macd)
    st.write(df_macd)
    st.write_stream(response)

    st.write("---")
    st.subheader('Dự đoán với chỉ số BOLL')
    response = forecast_price(question="Dựa vào các chỉ số trên phân tích giá chứng khoán trong thời gian tới,thời điểm, đưa ra giá mua vào và bán ra cổ phiếu cụ thể, giá cổ phiếu là VND", docs = df_boll)
    st.write(df_boll)
    st.write_stream(response)

    st.write("---")
    st.subheader('Dự đoán với chỉ số EMA')
    response = forecast_price(question="Dựa vào các chỉ số trên phân tích giá chứng khoán trong thời gian tới,thời điểm, đưa ra giá mua vào và bán ra cổ phiếu cụ thể, giá cổ phiếu là VND", docs = df_ma)
    st.write(df_ma)
    st.write_stream(response)
