import json
from bs4 import BeautifulSoup
import re
import requests

from langchain.llms import OpenAI
from langchain.agents import load_tools, AgentType, Tool
import yfinance as yf

from openai import OpenAI
import warnings
import os
warnings.filterwarnings("ignore")

<<<<<<< Updated upstream
OPENAI_API_KEY="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"

client = OpenAI(api_key=OPENAI_API_KEY)

from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo",openai_api_key=OPENAI_API_KEY)


# Fetch stock data from Yahoo Finance
def get_stock_price(ticker,history=5):
    # time.sleep(4) #To avoid rate limit error
    if "." in ticker:
        ticker=ticker.split(".")[0]
    ticker=ticker+".NS"
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    df=df[["Close","Volume"]]
    df.index=[str(x).split()[0] for x in list(df.index)]
    df.index.rename("Date",inplace=True)
    df=df[-history:]
    # print(df.columns)
    
    return df.to_string()
=======
def get_stock_price(ticker, history=5):
    try:
        if "." in ticker:
            ticker = ticker.split(".")[0]
        ticker = ticker + ".NS"
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        if df.empty:
            return f"No data available for {ticker}"
        df = df[["Close", "Volume"]]
        df.index = [str(x).split()[0] for x in list(df.index)]
        df.index.rename("Date", inplace=True)
        df = df[-history:]
        return df.to_string()
    except Exception as e:
        return f"Error retrieving data for {ticker}: {str(e)}"

print(get_stock_price("TITAN"))
>>>>>>> Stashed changes

# Script to scrap top5 googgle news for given company name
def google_query(search_term):
    if "news" not in search_term:
        search_term=search_term+" stock news"
    url=f"https://www.google.com/search?q={search_term}&cr=countryIN"
    url=re.sub(r"\s","+",url)
    return url

def get_recent_stock_news(company_name):
    # time.sleep(4) #To avoid rate limit error
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

    g_query=google_query(company_name)
    res=requests.get(g_query,headers=headers).text
    soup=BeautifulSoup(res,"html.parser")
    news=[]
    for n in soup.find_all("div","n0jPhd ynAwRc tNxQIb nDgy9d"):
        news.append(n.text)
    for n in soup.find_all("div","IJl0Z"):
        news.append(n.text)

    if len(news)>6:
        news=news[:4]
    else:
        news=news
    news_string=""
    for i,n in enumerate(news):
        news_string+=f"{i}. {n}\n"
    top5_news="Recent News:\n\n"+news_string
    
    return top5_news


# Fetch financial statements from Yahoo Finance
def get_financial_statements(ticker):
    # time.sleep(4) #To avoid rate limit error
    if "." in ticker:
        ticker=ticker.split(".")[0]
    else:
        ticker=ticker
    ticker=ticker+".NS"    
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[1]>=3:
        balance_sheet=balance_sheet.iloc[:,:3]    # Remove 4th years data
    balance_sheet=balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.to_string()
    return balance_sheet
<<<<<<< Updated upstream
=======
print(get_financial_statements("TATAPOWER.NS"))

# %% [markdown]
# ### Custom tools

# %%
from langchain.tools import DuckDuckGoSearchRun
search=DuckDuckGoSearchRun()
print(search("Stock news India"))

# %%
# Making tool list

tools=[
    Tool(
        name="get stock data",
        func=get_stock_price,
        description="Use when you are asked to evaluate or analyze a stock. This will output historic share price data. You should input the the stock ticker to it "
    ),
    Tool(
        name="DuckDuckGo Search",
        func=search.run,
        description="Use only when you need to get NSE/BSE stock ticker from internet, you can also get recent stock related news. Dont use it for any other analysis or task"
    ),
    Tool(
        name="get recent news",
        func=get_recent_stock_news,
        description="Use this to fetch recent news about stocks"
    ),

    Tool(
        name="get financial statements",
        func=get_financial_statements,
        description="Use this to get financial statement of the company. With the help of this data companys historic performance can be evaluaated. You should input stock ticker to it"
    ) 
>>>>>>> Stashed changes


#Openai function calling
function=[
        {
        "name": "get_company_Stock_ticker",
        "description": "This will get the indian NSE/BSE stock ticker of the company",
        "parameters": {
            "type": "object",
            "properties": {
                "ticker_symbol": {
                    "type": "string",
                    "description": "This is the stock symbol of the company.",
                },

                "company_name": {
                    "type": "string",
                    "description": "This is the name of the company given in query",
                }
            },
            "required": ["company_name","ticker_symbol"],
        },
    }
]


def get_stock_ticker(query):
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        temperature=0,
        messages=[{
            "role": "user",
            "content": f"Given the user request, what is the company name and the company stock ticker?: {query}?"
        }],
        functions=[
            {
                "name": "get_company_Stock_ticker",
                "description": "This will get the indian NSE/BSE stock ticker of the company",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker_symbol": {
                            "type": "string",
                            "description": "This is the stock symbol of the company.",
                        },
                        "company_name": {
                            "type": "string",
                            "description": "This is the name of the company given in query",
                        }
                    },
                    "required": ["company_name", "ticker_symbol"],
                },
            }
        ],
        function_call={"name": "get_company_Stock_ticker"},
    )
    message = response.choices[0].message
    arguments = json.loads(message.function_call.arguments)
    company_name = arguments["company_name"]
    company_ticker = arguments["ticker_symbol"]
    return company_name, company_ticker

<<<<<<< Updated upstream
=======
print(get_stock_ticker("How is ths stock of Paytm doing?"))

# %%
>>>>>>> Stashed changes
def Anazlyze_stock(query):
    #agent.run(query) Outputs Company name, Ticker
    Company_name,ticker=get_stock_ticker(query)
    print({"Query":query,"Company_name":Company_name,"Ticker":ticker})
    stock_data=get_stock_price(ticker,history=10)
    stock_financials=get_financial_statements(ticker)
    stock_news=get_recent_stock_news(Company_name)

    available_information=f"Stock Price: {stock_data}\n\nStock Financials: {stock_financials}\n\nStock News: {stock_news}"
    #available_information=f"Stock Financials: {stock_financials}\n\nStock News: {stock_news}"

    # print("\n\nAnalyzing.....\n")
    analysis=llm(f"Give detail stock analysis, Use the available data and provide investment recommendation. \
             The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer \
             User question: {query} \
             You have the following information available about {Company_name}. Write (5-8) pointwise investment analysis to answer user query, At the end conclude with proper explaination.Try to Give positives and negatives  : \
              {available_information} "
             )
    # print(analysis)

    return analysis

try:
    out = Anazlyze_stock("Shall I invest in Adani power right now?")
except Exception as e:
    print(f"An error occurred: {e}")