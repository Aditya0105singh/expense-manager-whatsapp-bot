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
