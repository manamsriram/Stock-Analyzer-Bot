# Stock Analyzer Bot 📈

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-AI-00B86B?logo=dataiku&logoColor=white)](https://langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT4-10A37F?logo=openai&logoColor=white)](https://platform.openai.com/)
[![yfinance](https://img.shields.io/badge/yfinance-Finance-73A1FB?logo=yahoo&logoColor=white)](https://pypi.org/project/yfinance/)
[![DuckDuckGo](https://img.shields.io/badge/DuckDuckGo-Search-FE7A16?logo=duckduckgo&logoColor=white)](https://duckduckgo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

> **AI-powered Bot to analyze stocks using LLMs, real-time/historical price, financials, and news.**  
> Get comprehensive investment insights from any device––no finance expertise required!

---

## 🔥 Overview

Stock Analyzer Bot uses LangChain, OpenAI LLMs, and live search/news/financial APIs to:
- Fetch & analyze **real-time/historical stock prices**
- Summarize **latest company news**
- Parse **financial statements**
- Return actionable investment analysis

---

## 🎯 Motivation

Stock analysis can be overwhelming for everyday investors. This bot centralizes data, automates analysis, and translates jargon, so you can focus on making smart decisions—faster.

---

## 🚀 Features

- **Conversational Q&A:** Ask investment questions in plain English.
- **Comprehensive Pipeline:** Prices, news, financials—all in one workflow.
- **Sentiment & Risk Analysis:** Latest market sentiment mixed with hard data.
- **Integrated Dashboard:** History, authentication, easy exploration.
- **Extensible Tools:** Add custom analysis, new data sources, or assets.

---

## 🛠️ Tech Stack

| [![Python](https://img.shields.io/badge/-Python-3A75A6?logo=python)](https://www.python.org/) | [![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io/) | [![LangChain](https://img.shields.io/badge/-LangChain-29B88A?logo=dataiku)](https://langchain.com/) | [![OpenAI](https://img.shields.io/badge/-OpenAI-10A37F?logo=openai)](https://openai.com/) | [![yfinance](https://img.shields.io/badge/-yfinance-73A1FB?logo=yahoo)](https://github.com/ranaroussi/yfinance) | [![DuckDuckGo](https://img.shields.io/badge/-DuckDuckGo-FE7A16?logo=duckduckgo)](https://duckduckgo.com/) | [![BeautifulSoup](https://img.shields.io/badge/-BeautifulSoup-4E8B93?logo=pypi)](https://www.crummy.com/software/BeautifulSoup/) | [![Pandas](https://img.shields.io/badge/-Pandas-150458?logo=pandas)](https://pandas.pydata.org/) |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|

---

## 📦 Installation

git clone https://github.com/manamsriram/Stock-Analyzer-Bot.git
cd Stock-Analyzer-Bot

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt


Add your OpenAI API key to a `.env` file:

OPENAI_API_KEY=sk-xxxxxxx


---

## 🖥️ Usage

streamlit run app.py

Open the Streamlit link in your browser, register/login, and start asking investment questions!

---

## 🗂️ Example Queries

- "Should I invest in Tesla this month?"
- "Show me financials and latest news for Yes Bank."
- "What's the outlook for Apple stock?"

---

## 🧰 Notebooks & Core Logic

- **stock_analyzer_bot.ipynb** : Tool definitions, LLM workflow examples, testing
- **app.py** : Streamlit web app, user authentication, query storage
- **tools/fetch_stock_info.py** : All major tools for price, news, financials

---

## 🏗️ Roadmap

- Add: Technical analysis, charting
- Support: More open-source LLMs (Claude, Mistral, Llama, ...), new markets
- Deploy: HuggingFace Spaces, Streamlit Cloud
- Modular: Crypto, mutual funds, asset categories
- Enhanced: Visual dashboard, search tools

---

## 👤 Author

Sri Ram Mannam  
[GitHub](https://github.com/manamsriram) | [LinkedIn](https://www.linkedin.com/in/sri-ram-mannam-8b61aa228/)

---

## 📜 License

MIT License. See [`LICENSE`](LICENSE).

---

## 🌐 Demo

Try it live: [stock-analyzer-bot.vercel.app](https://stock-analyzer-bot.vercel.app)

---
