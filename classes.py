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
