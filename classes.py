from typing import Annotated, List, Literal, TypedDict, Optional
from langchain_core.messages import AnyMessage
from langchain_core.pydantic_v1 import BaseModel, Field
import operator
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal


class Intent(BaseModel):
    intent: Literal["Expense", "Query", "Others"] = Field(
        description='Type of Query, if user want to add expense output should be "Expense", if user want to query about expenses output should be "Query". Else output should be "Others".'
    )


class Expense(BaseModel):
    price: float = Field(
        description="Price of the product purchased, in float. The currency should be INR; if not in INR, please convert to INR. If price is not provided return 0."
    )
    object: str = Field(
        description="Name/title of the product or object for which the expense was made. if no object is provided return None"
    )
    day: Literal[
        "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
    ] = Field(description="Day on which the expense was made.")
    dateAndTime: datetime = Field(
        description="The full datetime on which the expense was made (format: YYYY-MM-DD HH:MM:SS)."
    )
    otherDetails: str = Field(
        description="Here add any other details that are relevant to user requests."
    )


class Expenses(BaseModel):
    expenses: List[Expense] = Field(
        description="List of Expenses where each expense consist of fields like price, object, dateAndTime and otherdetails."
    )


class AppState(TypedDict):
    user_query: str
    intent: str
    messages: Annotated[list[AnyMessage], operator.add]
    expenses: Annotated[list[Expense], operator.add]
    new_expenses: list[Expense]
    query_response: str
    final_response: str
