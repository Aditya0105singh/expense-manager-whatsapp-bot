import warnings
warnings.filterwarnings("ignore")

from flask import Flask
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(port=5002)
