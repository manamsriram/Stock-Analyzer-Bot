# %%
import os
from bs4 import BeautifulSoup
import re
import requests
import warnings
from langchain.agents import load_tools, AgentType, Tool, initialize_agent

from langchain.agents import Tool
os.environ["OPENAI_API_KEY"] = "ENter your API key here"

warnings.filterwarnings("ignore")

# %%
import yfinance as yf
import time

# Fetch stock data from Yahoo Finance

def get_stock_price(ticker, exchange=None, history=5):
    try:
        time.sleep(4)  # Avoid rate limit
        
        # Handle exchange-specific tickers
        if exchange:
            if exchange.upper() == "NSE":
                ticker = f"{ticker}.NS"
            elif exchange.upper() == "BSE":
                ticker = f"{ticker}.BO"
            elif exchange.upper() in ["NYSE", "NASDAQ"]:
                ticker = ticker  # Keep original for US stocks
        else:
            # Default to NSE for backward compatibility
            ticker = f"{ticker}.NS"
            
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        
        if df.empty:
            return f"No data available for {ticker}"
            
        df = df[["Close", "Volume"]]
        df.index = [str(x).split()[0] for x in list(df.index)]
        df.index.rename("Date", inplace=True)
        
        if len(df) < history:
            return f"Only {len(df)} days of data available for {ticker}"
            
        df = df[-history:]
        print(ticker,exchange)
        return df.to_string()
        
    except Exception as e:
        return f"Error retrieving data for {ticker}: {str(e)}"

# %%
# Script to scrap top5 googgle news for given company name

def google_query(search_term):
    if "news" not in search_term:
        search_term = search_term + " stock news"
    url = f"https://www.google.com/search?q={search_term}&gl=in&tbm=nws&num=5"
    url = re.sub(r"\s", "+", url)
    return url

def get_recent_stock_news(company_name):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }
    
    try:
        g_query = google_query(company_name)
        response = requests.get(g_query, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        
        news_results = []
        # Look for news articles in Google News format
        articles = soup.select("div.SoaBEf")
        
        if not articles:
            return "No recent news found for " + company_name
            
        for article in articles[:4]:
            title = article.select_one("div.MBeuO")
            if title:
                news_results.append(title.get_text())
                
        news_string = "Recent News:\n\n"
        for i, news in enumerate(news_results):
            news_string += f"{i+1}. {news}\n"
            
        return news_string

    except Exception as e:
        return f"Error fetching news: {str(e)}"


# %%
# Fetch financial statements from Yahoo Finance

def get_financial_statements(ticker, exchange=None):
    try:
        time.sleep(4)  # Avoid rate limit
        
        # Handle exchange-specific tickers
        if exchange:
            if exchange.upper() == "NSE":
                ticker = f"{ticker}.NS"
            elif exchange.upper() == "BSE":
                ticker = f"{ticker}.BO"
            elif exchange.upper() in ["NYSE", "NASDAQ"]:
                ticker = ticker  # Keep original for US stocks
        else:
            ticker = f"{ticker}.NS"  # Default to NSE
            
        company = yf.Ticker(ticker)
        balance_sheet = company.balance_sheet
        
        if balance_sheet is None or balance_sheet.empty:
            return f"No financial data available for {ticker}"
            
        # Keep last 3 years of data
        if balance_sheet.shape[1] >= 3:
            balance_sheet = balance_sheet.iloc[:,:3]
            
        balance_sheet = balance_sheet.dropna(how="any")
        
        # Add income statement data
        try:
            income_stmt = company.income_stmt
            if income_stmt is not None and not income_stmt.empty:
                balance_sheet = balance_sheet.append(income_stmt.iloc[:5])
        except:
            pass
            
        return balance_sheet.to_string()
        
    except Exception as e:
        return f"Error retrieving financial data for {ticker}: {str(e)}"

# %% [markdown]
# ### Custom tools

# %%
from langchain.tools import DuckDuckGoSearchRun
search=DuckDuckGoSearchRun()


# %%
# Making tool list

def search_with_retry(query, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            result = search.run(query)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
                continue
            return f"Unable to search after {max_retries} attempts: {str(e)}"

tools = [
    Tool(
        name="get stock data",
        func=get_stock_price,
        description="Use when you are asked to evaluate or analyze a stock. Input format: ticker,exchange "
    ),
    Tool(
        name="DuckDuckGo Search",
        func=search_with_retry,
        description="Use to get stock ticker and exchange information. Search format: 'company name stock ticker exchange'"
    ),
    Tool(
        name="get recent news",
        func=get_recent_stock_news,
        description="Use this to fetch recent news about stocks"
    ),
    Tool(
        name="get financial statements",
        func=get_financial_statements,
        description="Get financial statements using ticker and exchange. Input format: ticker,exchange "
    )
]

# %%
#Adding predefine evaluation steps in the agent Prompt

new_prompt = """You are a financial advisor. Give stock recommendations for given query.
First identify the company name, stock ticker symbol, and the exchange it's listed on.
Answer the following questions as best you can. You have access to the following tools:

get stock data: Use for stock analysis. Requires ticker and exchange
DuckDuckGo Search: Use to find stock ticker and exchange information
get recent news: Use for recent stock news
get financial statements: Use for company financial analysis

steps- 
Note- if you fail in satisfying any step, move to next one
1) Get the company name and search for "company name stock ticker exchange" on internet. Extract stock ticker and exchange (NSE/BSE/NYSE/NASDAQ)
2) Use "get stock data" tool with ticker and exchange to gather stock info
3) Get company's financial data using "get financial statements"
4) Use "get recent news" tool for latest stock news
5) Analyze the stock based on gathered data and provide detailed investment analysis with numbers and reasons

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do, following steps above
Action: the action to take, should be one of [get stock data, DuckDuckGo Search, get recent news, get financial statements]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""



# %%
from langchain.chat_models import ChatOpenAI
from openai import OpenAI

OPENAI_API_KEY="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"

client = OpenAI(api_key=OPENAI_API_KEY)

def create_stock_analyzer():
    # Initialize the LLM
    llm = ChatOpenAI(
        temperature=0, 
        model_name="gpt-4-turbo",
        openai_api_key=OPENAI_API_KEY
    )
    
    # Initialize the agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={
            "prefix": new_prompt
        }
    )
    
    return agent

# %%
#Openai function calling

import json

def get_stock_ticker(query):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "user",
                "content": f"Given the user request, what is the company name, stock ticker, and exchange?: {query}?"
            }],
            functions=[{
                "name": "get_company_Stock_ticker",
                "description": "This will get the stock ticker of the company",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticker_symbol": {
                            "type": "string",
                            "description": "Stock symbol of the company"
                        },
                        "company_name": {
                            "type": "string",
                            "description": "Name of the company"
                        },
                        "exchange": {
                            "type": "string",
                            "description": "Stock exchange (NSE, BSE, NYSE, NASDAQ)",
                            "enum": ["NSE", "BSE", "NYSE", "NASDAQ"]
                        }
                    },
                    "required": ["company_name", "ticker_symbol", "exchange"]
                }
            }],
            function_call={"name": "get_company_Stock_ticker"}
        )
        
        arguments = json.loads(response.choices[0].message.function_call.arguments)
        return arguments["company_name"], arguments["ticker_symbol"], arguments["exchange"]
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None


# %%
def Analyze_stock(query):
    agent = create_stock_analyzer()
    try:
        response = agent.run(query)
        return response
    except Exception as e:
        return f"An error occurred during analysis: {str(e)}"

