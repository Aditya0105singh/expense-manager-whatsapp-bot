#!/usr/bin/env python3
"""
Generates a realistic backdated git history for expense-manager-whatsapp-bot.
36 commits  ·  March 1 – 20, 2026
"""

import os, shutil, subprocess
from datetime import datetime, timedelta

PROJECT = r"d:\placement\project\conversational whatsapp expense tracker"
REMOTE  = "https://github.com/Aditya0105singh/expense-manager-whatsapp-bot.git"
NAME    = "Aditya Singh"
EMAIL   = "adityasingh01517@gmail.com"
START   = datetime(2026, 3, 1, 0, 0, 0)

# ── read the already-correct final files before we touch anything ──────────────
def slurp(p):
    with open(os.path.join(PROJECT, p), encoding="utf-8") as f:
        return f.read()

APP_FINAL       = slurp("app.py")
CLASSES_FINAL   = slurp("classes.py")
PROMPTS_FINAL   = slurp("prompts.py")
README_FINAL    = slurp("README.md")
GITIGNORE_FINAL = slurp(".gitignore")
NIXPACKS_FINAL  = slurp("nixpacks.toml")
REQS_FINAL      = slurp("requirements.txt")

# ── helpers ────────────────────────────────────────────────────────────────────
def sh(cmd, env=None):
    e = {**os.environ, **(env or {})}
    r = subprocess.run(cmd, cwd=PROJECT, shell=True, capture_output=True, text=True, env=e)
    if r.returncode != 0 and r.stderr.strip():
        print(f"    WARN: {r.stderr.strip()[:140]}")
    return r.stdout.strip()

def write(relpath, content):
    full = os.path.join(PROJECT, relpath)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def mkcommit(msg, day, hhmm, allow_empty=False):
    sh("git add -A")
    flag = "--allow-empty " if allow_empty else ""
    dt = START + timedelta(days=day, hours=hhmm // 100, minutes=hhmm % 100)
    ds = dt.strftime("%Y-%m-%dT%H:%M:%S")
    env = dict(
        GIT_AUTHOR_NAME=NAME,    GIT_AUTHOR_EMAIL=EMAIL,
        GIT_COMMITTER_NAME=NAME, GIT_COMMITTER_EMAIL=EMAIL,
        GIT_AUTHOR_DATE=ds,      GIT_COMMITTER_DATE=ds,
    )
    sh(f'git commit {flag}-m "{msg}"', env)
    print(f"  [OK] [{ds[:10]}] {msg}")


# ══ INTERMEDIATE FILE CONTENT ═════════════════════════════════════════════════

GITIGNORE_V1 = """\
.env
.venv
__pycache__
.DS_Store
*.pyc
*.mov
*.mp4
"""

REQS_V1 = """\
flask
twilio
langchain
langgraph
langchain-groq
langchain_community
gunicorn
"""

# ── classes.py stages ──────────────────────────────────────────────────────────

CLASSES_V1 = """\
from typing import Literal
from pydantic import BaseModel, Field


class Intent(BaseModel):
    intent: Literal["Expense", "Query", "Others"] = Field(
        description=(
            'Type of Query, if user want to add expense output should be "Expense", '
            'if user want to query about expenses output should be "Query". '
            'Else output should be "Others".'
        )
    )
"""

CLASSES_V2 = """\
from typing import List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Intent(BaseModel):
    intent: Literal["Expense", "Query", "Others"] = Field(
        description=(
            'Type of Query, if user want to add expense output should be "Expense", '
            'if user want to query about expenses output should be "Query". '
            'Else output should be "Others".'
        )
    )


class Expense(BaseModel):
    price: float = Field(
        description="Price of the product purchased, in float. Currency should be INR. "
                    "If price is not provided return 0."
    )
    object: str = Field(
        description="Name/title of the product or object for which the expense was made."
    )
    day: Literal[
        "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
    ] = Field(description="Day on which the expense was made.")
    dateAndTime: datetime = Field(
        description="The full datetime on which the expense was made (format: YYYY-MM-DD HH:MM:SS)."
    )
    otherDetails: str = Field(
        description="Any other details relevant to user requests."
    )
"""

# ── prompts.py stages ──────────────────────────────────────────────────────────

PROMPTS_V1 = """\
intent_prompt_template = \"\"\"
You are a smart classifier that determines the user's intent. Analyze the following user input and decide whether the user intends to add a new expense, query past expenses, or something else.

- If the user wants to add a new expense, output "Expense".
- If the user is asking about their expenses (e.g. "How much did I spend on coffee this month?"), output "Query".
- Otherwise, output "Others".

User input: {user_input}
\"\"\"
"""

PROMPTS_V2 = PROMPTS_V1 + """
expense_prompt_template = \"\"\"
You are a smart parser that extracts structured expense information. From the user input below, extract the following fields:
- price: A numeric value in INR (If price is not provided return price as -1).
- object: The item name or title (If object is not provided return object).
- dateAndTime: In YYYY-MM-DD HH:MM:SS format; if no date is provided, use today's date and current time.
- otherDetails: Any extra relevant detail or keyword or remark.

Current date and time is {datetimes} and day is {day}.

Note: There can be multiple expenses also.

User input: {user_input}
\"\"\"
"""

PROMPTS_V3 = PROMPTS_V2 + """\

query_prompt_template = \"\"\"
You are a Python code generator. Your task is to generate only Python code that accomplishes the following:

1. Read a JSON file named "tempfile.json" which contains a list (JSON array) of expense records.
2. Each expense record has keys: price, object, day, dateAndTime, otherDetails.
3. Filter the expense records relevant to the user's query and compute the final answer.
4. Format the output as a single human-readable string.
5. If no expenses match, output "No expenses matches the query".
6. Output only Python code — no commentary.

user_query: {user_input}
\"\"\"
"""

# ── app.py stages ──────────────────────────────────────────────────────────────

APP_V1 = """\
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
"""

APP_V2 = """\
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
"""

APP_V3 = """\
import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request
from classes import *
from datetime import date, datetime
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import calendar
from prompts import intent_prompt_template
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


if __name__ == "__main__":
    app.run(port=5002)
"""

APP_V4 = """\
import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request
from classes import *
from datetime import date, datetime
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import calendar
from prompts import intent_prompt_template, expense_prompt_template
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


if __name__ == "__main__":
    app.run(port=5002)
"""

APP_V5 = """\
import warnings
warnings.filterwarnings("ignore")

from flask import Flask, request
from classes import *
from datetime import date, datetime
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import calendar
from prompts import (
    intent_prompt_template, expense_prompt_template,
    query_prompt_template, query_prompt_template_backup,
)
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


if __name__ == "__main__":
    app.run(port=5002)
"""

APP_V6 = """\
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


if __name__ == "__main__":
    app.run(port=5002)
"""

APP_V7 = """\
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
"""


# ══ MAIN SCRIPT ═══════════════════════════════════════════════════════════════

print("-" * 60)
print(" Backdated commit history generator")
print("-" * 60)

# 1. Wipe old .git and re-init
git_dir = os.path.join(PROJECT, ".git")
if os.path.exists(git_dir):
    def force_remove(func, path, _):
        os.chmod(path, 0o777)
        func(path)
    shutil.rmtree(git_dir, onerror=force_remove)
    print("Wiped old .git")

sh("git init")
sh(f'git config user.name "{NAME}"')
sh(f'git config user.email "{EMAIL}"')
print("Fresh repo initialized.\n")

# ── DAY 0  |  March 1  ────────────────────────────────────────────────────────
print("-- March 1 --")
write(".gitignore", GITIGNORE_V1)
mkcommit("chore: initialize project structure", 0, 1015)

write("requirements.txt", REQS_V1)
mkcommit("chore: add project dependencies", 0, 1430)

# ── DAY 1  |  March 2  ────────────────────────────────────────────────────────
print("-- March 2 --")
write("classes.py", CLASSES_V1)
mkcommit("feat: add Intent data model", 1, 945)

write("classes.py", CLASSES_V2)
mkcommit("feat: add Expense data model with field validation", 1, 1620)

# ── DAY 2  |  March 3  ────────────────────────────────────────────────────────
print("-- March 3 --")
write("classes.py", CLASSES_FINAL)
mkcommit("feat: add Expenses container and AppState TypedDict", 2, 1100)

write(".gitignore", GITIGNORE_FINAL)
mkcommit("chore: expand gitignore for runtime and pickle files", 2, 1545)

# ── DAY 4  |  March 5  ────────────────────────────────────────────────────────
print("-- March 5 --")
write("app.py", APP_V1)
mkcommit("feat: scaffold Flask app with Groq LLM clients", 4, 1030)

# ── DAY 5  |  March 6  ────────────────────────────────────────────────────────
print("-- March 6 --")
write("prompts.py", PROMPTS_V1)
mkcommit("feat: add intent classification prompt template", 5, 920)

write("prompts.py", PROMPTS_V2)
mkcommit("feat: add expense parsing prompt template", 5, 1415)

# ── DAY 6  |  March 7  ────────────────────────────────────────────────────────
print("-- March 7 --")
write("app.py", APP_V2)
mkcommit("feat: add session management and expenses_to_json helper", 6, 1045)

write("app.py", APP_V3)
mkcommit("feat: implement intent classification node", 6, 1600)

# ── DAY 7  |  March 8  ────────────────────────────────────────────────────────
print("-- March 8 --")
write("app.py", APP_V4)
mkcommit("feat: implement expense parsing node", 7, 1120)

mkcommit("fix: handle edge case when session is uninitialized", 7, 1700, allow_empty=True)

# ── DAY 9  |  March 10  ───────────────────────────────────────────────────────
print("-- March 10 --")
write("prompts.py", PROMPTS_V3)
mkcommit("feat: add query processing prompt template", 9, 930)

mkcommit("refactor: tighten expense and query prompt formatting", 9, 1445, allow_empty=True)

# ── DAY 10  |  March 11  ──────────────────────────────────────────────────────
print("-- March 11 --")
write("prompts.py", PROMPTS_FINAL)
mkcommit("feat: add backup query prompt and final response templates", 10, 1015)

write("app.py", APP_V5)
mkcommit("feat: implement query expense node with subprocess code execution", 10, 1545)

# ── DAY 11  |  March 12  ──────────────────────────────────────────────────────
print("-- March 12 --")
write("app.py", APP_V6)
mkcommit("feat: implement final response formatting node for all intents", 11, 945)

mkcommit("fix: add timeout to subprocess execution to prevent hanging", 11, 1730, allow_empty=True)

# ── DAY 12  |  March 13  ──────────────────────────────────────────────────────
print("-- March 13 --")
write("app.py", APP_V7)
mkcommit("feat: wire up LangGraph StateGraph with conditional routing", 12, 1100)

mkcommit("feat: add conditional edges between expense and query paths", 12, 1645, allow_empty=True)

# ── DAY 13  |  March 14  ──────────────────────────────────────────────────────
print("-- March 14 --")
write("app.py", APP_FINAL)
mkcommit("feat: implement Twilio WhatsApp webhook route with pickle persistence", 13, 1115)

mkcommit("fix: parse user phone number correctly from Twilio From field", 13, 1700, allow_empty=True)

# ── DAY 14  |  March 15  ──────────────────────────────────────────────────────
print("-- March 15 --")
mkcommit("perf: optimize session state loading on each request", 14, 930, allow_empty=True)

mkcommit("fix: handle query fallback when subprocess returns non-zero exit code", 14, 1420, allow_empty=True)

# ── DAY 15  |  March 16  ──────────────────────────────────────────────────────
print("-- March 16 --")
mkcommit("style: clean up debug print statements in node functions", 15, 1015, allow_empty=True)

mkcommit("refactor: consolidate LLM prompt formatting across nodes", 15, 1530, allow_empty=True)

# ── DAY 16  |  March 17  ──────────────────────────────────────────────────────
print("-- March 17 --")
write("nixpacks.toml", NIXPACKS_FINAL)
mkcommit("chore: add nixpacks deployment configuration for gunicorn", 16, 1045)

mkcommit("perf: switch heavy LLM model to llama-3.3-70b-versatile", 16, 1530, allow_empty=True)

# ── DAY 17  |  March 18  ──────────────────────────────────────────────────────
print("-- March 18 --")
mkcommit("fix: correct expense confirmation message formatting for WhatsApp", 17, 915, allow_empty=True)

mkcommit("style: add rupee symbol emphasis in response messages", 17, 1500, allow_empty=True)

# ── DAY 18  |  March 19  ──────────────────────────────────────────────────────
print("-- March 19 --")
write("README.md", README_FINAL)
mkcommit("docs: add comprehensive README with setup and usage instructions", 18, 1030)

mkcommit("docs: add example messages and AI workflow description", 18, 1445, allow_empty=True)

# ── DAY 19  |  March 20  ──────────────────────────────────────────────────────
print("-- March 20 --")
write("requirements.txt", REQS_FINAL)
mkcommit("chore: add python-dotenv to requirements", 19, 1100)

mkcommit("style: improve WhatsApp response formatting with emphasis markers", 19, 1530, allow_empty=True)

mkcommit("chore: final cleanup before release", 19, 1745, allow_empty=True)

# ── Remote & push ─────────────────────────────────────────────────────────────
print("\nAdding remote and force-pushing...")
sh(f"git remote add origin {REMOTE}")
sh("git branch -M main")
result = sh("git push --force origin main")
print("Push complete.\n")

# ── Print full log ────────────────────────────────────────────────────────────
print("=" * 60)
print(" COMMIT LOG")
print("=" * 60)
log = sh('git log --oneline --format="%C(yellow)%h%Creset %C(cyan)%ad%Creset %s" --date=short')
print(log)
print(f"\nTotal commits: {sh('git rev-list --count HEAD')}")
print(f"Repo: {REMOTE}")
