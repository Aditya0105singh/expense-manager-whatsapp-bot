import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request
from classes import *
from datetime import date, datetime
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import calendar
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
state_db = {}

light_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)
heavy_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


def expenses_to_json(expenses: Expenses) -> dict:
    expenses_json = []
    for expense in expenses:
        expenses_json.append({
            "price": expense.price,
            "object": expense.object,
            "day": expense.day,
            "dateAndTime": str(expense.dateAndTime),
            "otherDetails": expense.otherDetails,
        })
    return expenses_json


def get_session_history(session_id: str) -> AppState:
    if session_id not in state_db:
        state_db[session_id] = AppState()
    return state_db[session_id]


if __name__ == "__main__":
    app.run(port=5002)
