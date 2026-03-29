import yfinance as yf
from openai import OpenAI
import os
import json
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.utils import embedding_functions

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==========================================
# 🧠 VECTOR DATABASE SETUP
# ==========================================
print("📦 [SYSTEM] Initializing Local Vector Database (ChromaDB)...")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection(
    name="company_knowledge",
    embedding_function=openai_ef
)


# ==========================================
# 🛠️ AGENT TOOLS
# ==========================================

def calculate_financial_scenarios(current_price: float, base_growth: float):
    print(f"🔧 [TOOL 1] Calculating scenarios (Growth: {base_growth}%)...")
    return {
        "base_case": round(current_price * (1 + base_growth / 100), 2),
        "upside_case": round(current_price * (1 + (base_growth + 10) / 100), 2),
        "downside_case": round(current_price * (1 + (base_growth - 15) / 100), 2)
    }


def fetch_market_news(ticker: str):
    print(f"📰 [TOOL 2] Fetching Yahoo Finance news for {ticker}...")
    try:
        news_items = yf.Ticker(ticker).news[:2]
        return [{"title": n.get('title')} for n in news_items]
    except:
        return [{"title": "News fetch failed."}]


def fetch_fundamentals_alphavantage(ticker: str):
    print(f"📊 [TOOL 3] Fetching fundamentals from Alpha Vantage for {ticker}...")
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
    try:
        res = requests.get(url).json()
        if "Symbol" not in res: return {"error": "API limit reached"}
        return {"EBITDA": res.get("EBITDA", "N/A"), "PE_Ratio": res.get("PERatio", "N/A")}
    except Exception as e:
        return {"error": str(e)}


def get_company_insights_via_rag(url: str, ticker: str):
    """web -> chunk -> vector search"""
    print(f"🌐🔎 [TOOL 4 - RAG] Executing Auto-RAG pipeline for {url}...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        chunk = text[:3000]  # 截取前 3000 字
        collection.upsert(
            documents=[chunk],
            metadatas=[{"source": url, "ticker": ticker, "type": "strategy"}],
            ids=[f"{ticker}_auto_rag_1"]
        )
        print("💾 [DATABASE] Web data embedded and saved to ChromaDB!")

        query = "What is the company's core product, main business, and strategic positioning?"
        results = collection.query(
            query_texts=[query],
            n_results=1,
            where={"ticker": ticker}
        )

        if results['documents'] and results['documents'][0]:
            print("✅ [RAG] Relevant context successfully retrieved from DB!")
            return {"retrieved_context": results['documents'][0][0][:1500]}
        return {"error": "Ingested successfully but retrieval yielded no specific strategy."}
    except Exception as e:
        return {"error": f"Auto-RAG failed: {str(e)}"}


# ==========================================
# 🚀 AGENT PIPELINE
# ==========================================

def run_agentic_pipeline(ticker: str):
    print(f"\n🚀 [PIPELINE START] Booting Agent for {ticker}...")

    stock = yf.Ticker(ticker)
    info = stock.info
    current_price = info.get('currentPrice', info.get('regularMarketPrice', 100.0))
    company_name = info.get('longName', ticker)
    website = info.get('website', '')

    tools = [
        {"type": "function", "function": {"name": "calculate_financial_scenarios", "parameters": {"type": "object",
                                                                                                  "properties": {
                                                                                                      "current_price": {
                                                                                                          "type": "number"},
                                                                                                      "base_growth": {
                                                                                                          "type": "number"}},
                                                                                                  "required": [
                                                                                                      "current_price",
                                                                                                      "base_growth"]}}},
        {"type": "function", "function": {"name": "fetch_market_news",
                                          "parameters": {"type": "object", "properties": {"ticker": {"type": "string"}},
                                                         "required": ["ticker"]}}},
        {"type": "function", "function": {"name": "fetch_fundamentals_alphavantage",
                                          "parameters": {"type": "object", "properties": {"ticker": {"type": "string"}},
                                                         "required": ["ticker"]}}}
    ]

    # 动态加载 RAG 工具
    if website:
        tools.append({"type": "function", "function": {"name": "get_company_insights_via_rag",
                                                       "parameters": {"type": "object",
                                                                      "properties": {"url": {"type": "string"},
                                                                                     "ticker": {"type": "string"}},
                                                                      "required": ["url", "ticker"]}}})

    messages = [
        {"role": "system",
         "content": "You are an Elite Finance Agent. You MUST use all available tools in parallel to gather maximum data (math scenarios, news, fundamentals, and RAG insights). Then, synthesize a brilliant, data-driven final report."},
        {"role": "user", "content": f"Analyze {company_name} ({ticker}). Price: ${current_price}. Website: {website}."}
    ]

    print("🤖 [AGENT] Reasoning and routing tools in parallel...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    messages.append(response_message)
    scenarios_data = {}

    if response_message.tool_calls:
        print(f"🤖 [AGENT ACTION] Firing {len(response_message.tool_calls)} tools simultaneously...")
        for tool_call in response_message.tool_calls:
            fname = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            tool_result = {}
            if fname == "calculate_financial_scenarios":
                scenarios_data = calculate_financial_scenarios(args.get("current_price"), args.get("base_growth"))
                tool_result = scenarios_data
            elif fname == "fetch_market_news":
                tool_result = fetch_market_news(args.get("ticker", ticker))
            elif fname == "fetch_fundamentals_alphavantage":
                tool_result = fetch_fundamentals_alphavantage(args.get("ticker", ticker))
            elif fname == "get_company_insights_via_rag":
                tool_result = get_company_insights_via_rag(args.get("url", website), args.get("ticker", ticker))

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": fname,
                "content": json.dumps(tool_result)
            })

        print("🤖 [AGENT] All tool data collected. Synthesizing Final Advisory Report...")
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        final_report = second_response.choices[0].message.content
    else:
        final_report = response_message.content

    return {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "current_price": current_price,
        "scenarios": {"base_case": {"price": scenarios_data.get("base_case", current_price), "desc": "Agent modeled"},
                      "upside_case": {"price": scenarios_data.get("upside_case", current_price),
                                      "desc": "Agent modeled"},
                      "downside_case": {"price": scenarios_data.get("downside_case", current_price),
                                        "desc": "Agent modeled"}},
        "ai_report": final_report
    }


