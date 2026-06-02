import warnings

warnings.filterwarnings("ignore")

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from classes import *
from datetime import date
from datetime import datetime
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import calendar
from prompts import *
from dotenv import load_dotenv
import os
import json
from langgraph.graph import END, StateGraph
import subprocess
from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage
import pickle

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
        expense_obj = {
            "price": expense.price,
            "object": expense.object,
            "day": expense.day,
            "dateAndTime": str(expense.dateAndTime),
            "otherDetails": expense.otherDetails,
        }
        expenses_json.append(expense_obj)
    return expenses_json


def get_session_history(session_id: str) -> AppState:
    if session_id not in state_db:
        state_db[session_id] = AppState()
    return state_db[session_id]


def intent_classification_node(state: AppState):

    intent_prompt = PromptTemplate(
        input_variables=["user_input"], template=intent_prompt_template
    )

    user_message = state["user_query"]

    prompt = intent_prompt.format(user_input=user_message)

    structured_llm = light_llm.with_structured_output(Intent)

    parsed_data = structured_llm.invoke(prompt)

    print(parsed_data)

    return {"intent": parsed_data.intent}


def parse_expense_node(state: AppState):
    expense_prompt = PromptTemplate(
        input_variables=["user_input", "datetimes", "day"],
        template=expense_prompt_template,
    )
    user_message = state["user_query"]
    prompt = expense_prompt.format(
        user_input=user_message,
        datetimes=datetime.today(),
        day=calendar.day_name[date.today().weekday()],
    )

    structured_llm = light_llm.with_structured_output(Expenses)

    parsed_data = structured_llm.invoke(prompt)

    print(parsed_data)
    return {"expenses": parsed_data.expenses, "new_expenses": parsed_data.expenses}


def sum_expenses(list_of_expenses: List[int]) -> str:
    return f"Sum of All the expenses is: {sum(list_of_expenses)}"


def query_expense_node(state: AppState):
    query_prompt = PromptTemplate(
        input_variables=["user_input"], template=query_prompt_template
    )

    expenses_json = expenses_to_json(state["expenses"])

    user_message = state["user_query"]
    with open("tempfile.json", "w") as f:
        json.dump(expenses_json, f, default=str)
    prompt = query_prompt.format(
        user_input=user_message,
    )
    output_code = heavy_llm.invoke(prompt)
    if "```python" in output_code.content:
        output_code = output_code.content[9:-3]

    with open("temp.py", "w") as f:
        f.write(output_code)

    query_response = subprocess.run(
        ["python3", "temp.py"], capture_output=True, text=True, timeout=10
    )
    print("--------------------------------")
    print(output_code)
    print("--------------------------------")
    print(query_response)
    print("--------------------------------")
    if query_response.returncode != 0:
        query_prompt = PromptTemplate(
            input_variables=["user_input", "expenses_data"],
            template=query_prompt_template_backup,
        )
        prompt = query_prompt.format(
            user_input=user_message, expenses_data=str(expenses_json)
        )
        query_response = heavy_llm.invoke(prompt).content
    else:
        query_response = query_response.stdout
    print(query_response)
    print("--------------------------------")

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
            input_variables=["user_query"],
            template=final_response_prompt["Others"],
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
try:
    png_graph = graph_app.get_graph().draw_mermaid_png()
    with open("my_graph.png", "wb") as f:
        f.write(png_graph)
    print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
except Exception:
    print("Graph image generation skipped.")


@app.route("/", methods=["POST"])
def main():
    global state_db

    state_db_file = "state_db.pkl"
    if not (os.path.exists(state_db_file)):
        with open(state_db_file, "wb") as f:
            pickle.dump(state_db, f)
    else:
        with open(state_db_file, "rb") as f:
            state_db = pickle.load(f)

    user_msg = request.values.get("Body", "")
    user = request.values.get("From", "").split(":")[1]

    state = get_session_history(user)
    state["user_query"] = user_msg

    state = graph_app.invoke(state)

    final_response = state["final_response"]

    state_db[user] = state

    with open(state_db_file, "wb") as f:
        pickle.dump(state_db, f)

    response = MessagingResponse()
    response.message(final_response)

    return str(response)


if __name__ == "__main__":
    app.run(port=5002)
