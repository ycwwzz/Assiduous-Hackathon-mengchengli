# Assiduous-Hackathon-mengchengli


An AI-driven strategic advisory platform that automates investment research, financial scenario modeling, and report generation using an Agentic RAG architecture.

## 🏗️ Architecture Overview

The system is built on a modern decoupling architecture, utilizing a "Native LLM Tool Calling" approach over heavy frameworks to maximize stability and speed.

* **Frontend (Vue.js):** Provides a reactive UI for users to input tickers. It handles real-time state management.
* **Backend (FastAPI + Python):** Serves as the orchestration layer. It exposes endpoints for the frontend and triggers the AI Agent pipeline.
* **AI Engine (OpenAI + Tool Calling):** The core "Brain." It is instructed to route tasks simultaneously using native Function Calling.
* **Tool Ecosystem:**
    * **Math Tool:** Pure Python financial calculator for Target Prices (Base, Upside, Downside).
    * **Data Tools:** Real-time integration with Yahoo Finance (yfinance) and Alpha Vantage APIs.
    * **Auto-RAG Engine:** A fused tool that scrapes company websites (BeautifulSoup), chunks text, ingests it into a local Vector Database (**ChromaDB**), and retrieves strategic positioning—all within a single LLM tool invocation to prevent multi-step deadlocks.
* **Export Module (FPDF2):** Generates instant, formatted PDF reports from the LLM's final synthesis.

## ⚙️ How to Run

**Prerequisites:** Docker and Docker Compose installed.

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <repo-folder>
    ```
2.  **Environment Variables:**
    Create a `.env` file in the `backend/` directory with the following keys:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key # Optional, falls back to 'demo'
    ```
3.  **Build and Run via Docker Compose:**
    ```bash
    docker-compose up --build
    ```
4.  **Access the Application:**
    * Frontend UI: `http://localhost:8080`
    * Backend API Docs (Swagger): `http://localhost:8000/docs`

## ⚠️ Limitations

* **Scraping Constraints:** To ensure system stability and avoid Docker I/O crashes caused by heavy headless browsers (like Chromium/Playwright), we use lightweight `BeautifulSoup`. It may struggle with heavily JavaScript-rendered SPAs (Single Page Applications).
* **API Rate Limits:** The Alpha Vantage free tier is highly restrictive. If the limit is reached, the Agent will gracefully degrade and note the missing fundamental data in its report.
* **LLM Predictability:** GPT-3.5 occasionally skips mathematical tool calls.

## 🔌 Third-Party Data & APIs

* **OpenAI API (`gpt-3.5-turbo` & `text-embedding-3-small`):** Core reasoning, routing, and text embedding.
* **Yahoo Finance (`yfinance` library):** Real-time stock prices and latest market news headlines.
* **Alpha Vantage API:** Deep company fundamentals (EBITDA, P/E Ratios).
* **ChromaDB:** Local, persistent vector database for internal knowledge retrieval.