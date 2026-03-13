import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request
from classes import *
from datetime import date, datetime
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import calendar
from prompts import *
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from dotenv import load_dotenv
import os
import json
import subprocess

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


def intent_classification_node(state: AppState):
    intent_prompt = PromptTemplate(
        input_variables=["user_input"], template=intent_prompt_template
    )
    prompt = intent_prompt.format(user_input=state["user_query"])
    parsed_data = light_llm.with_structured_output(Intent).invoke(prompt)
    print(parsed_data)
    return {"intent": parsed_data.intent}


def parse_expense_node(state: AppState):
    expense_prompt = PromptTemplate(
        input_variables=["user_input", "datetimes", "day"],
        template=expense_prompt_template,
    )
    prompt = expense_prompt.format(
        user_input=state["user_query"],
        datetimes=datetime.today(),
        day=calendar.day_name[date.today().weekday()],
    )
    parsed_data = light_llm.with_structured_output(Expenses).invoke(prompt)
    print(parsed_data)
    return {"expenses": parsed_data.expenses, "new_expenses": parsed_data.expenses}


def query_expense_node(state: AppState):
    expenses_json = expenses_to_json(state["expenses"])
    user_message = state["user_query"]
    with open("tempfile.json", "w") as f:
        json.dump(expenses_json, f, default=str)
    q_prompt = PromptTemplate(
        input_variables=["user_input"], template=query_prompt_template
    )
    output_code = heavy_llm.invoke(q_prompt.format(user_input=user_message))
    if "```python" in output_code.content:
        output_code = output_code.content[9:-3]
    with open("temp.py", "w") as f:
        f.write(output_code)
    result = subprocess.run(
        ["python3", "temp.py"], capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        backup = PromptTemplate(
            input_variables=["user_input", "expenses_data"],
            template=query_prompt_template_backup,
        )
        query_response = heavy_llm.invoke(
            backup.format(user_input=user_message, expenses_data=str(expenses_json))
        ).content
    else:
        query_response = result.stdout
    return {"query_response": query_response}


def final_response_node(state: AppState):
    if state["intent"] == "Expense":
        final_prompt = PromptTemplate(
            input_variables=["new_expenses"], template=final_response_prompt["Expense"]
        )
        prompt = final_prompt.format(
            new_expenses=str(expenses_to_json(state["new_expenses"]))
        )
    elif state["intent"] == "Query":
        final_prompt = PromptTemplate(
            input_variables=["query_response", "user_query"],
            template=final_response_prompt["Query"],
        )
        prompt = final_prompt.format(
            query_response=state["query_response"], user_query=state["user_query"]
        )
    else:
        final_prompt = PromptTemplate(
            input_variables=["user_query"], template=final_response_prompt["Others"]
        )
        prompt = final_prompt.format(user_query=state["user_query"])

    prompt = HumanMessage(prompt)
    response = heavy_llm.invoke(state["messages"] + [prompt])
    return {"final_response": response.content, "messages": [response]}


def intent_check(state: AppState):
    return state["intent"]


graph = StateGraph(AppState)
graph.support_multiple_edges = True

graph.add_node("intent_classifier_node", intent_classification_node)
graph.add_node("parse_expense_node", parse_expense_node)
graph.add_node("query_expense_node", query_expense_node)
graph.add_node("final_response_node", final_response_node)

graph.add_conditional_edges(
    "intent_classifier_node",
    intent_check,
    {
        "Query": "query_expense_node",
        "Expense": "parse_expense_node",
        "Others": "final_response_node",
    },
)

graph.add_edge("parse_expense_node", "final_response_node")
graph.add_edge("query_expense_node", "final_response_node")

graph.set_entry_point("intent_classifier_node")
graph.set_finish_point("final_response_node")

graph_app = graph.compile()
print("LangGraph workflow compiled successfully.")

if __name__ == "__main__":
    app.run(port=5002)
