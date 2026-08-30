from fastapi import FastAPI
from pydantic import BaseModel

import pandas as pd
import requests

from backend.finance import analyze_transactions


app = FastAPI(
    title="FinSight AI",
    description="Local Personal Finance Analysis API",
    version="1.0"
)


class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    type: str


class TransactionRequest(BaseModel):
    transactions: list[Transaction]


class AIAnalysisRequest(BaseModel):
    financial_summary: dict


@app.get("/")
def home():

    return {
        "message": "FinSight AI API is running"
    }


@app.post("/analyze")
def analyze(request: TransactionRequest):

    data = [
        {
            "Date": transaction.date,
            "Description": transaction.description,
            "Amount": transaction.amount,
            "Type": transaction.type
        }
        for transaction in request.transactions
    ]

    df = pd.DataFrame(data)

    result = analyze_transactions(df)

    return result


@app.post("/ai-analysis")
def ai_analysis(request: AIAnalysisRequest):

    summary = request.financial_summary

    prompt = f"""
You are a personal finance spending pattern analyst.

Analyze ONLY the financial information provided below.

Rules:
1. Do not invent numbers.
2. Do not assume missing information.
3. Do not provide investment advice.
4. Do not recommend financial products.
5. Use only the provided data.
6. Give concise and practical insights.

Financial Summary:

Total Income: ₹{summary.get("income", 0)}
Total Expenses: ₹{summary.get("expenses", 0)}
Savings: ₹{summary.get("savings", 0)}

Spending by Category:

{summary.get("categories", {})}

Provide:

1. Spending summary
2. Top spending category
3. Important spending patterns
4. Potential concerns
5. Three practical suggestions
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:4b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        return {
            "analysis": result["response"]
        }

    except requests.exceptions.RequestException as e:

        return {
            "error": f"Could not connect to Ollama: {str(e)}"
        }