intent_prompt_template = """
You are a smart classifier that determines the user's intent. Analyze the following user input and decide whether the user intends to add a new expense, query past expenses, or something else.

- If the user wants to add a new expense, output "Expense".
- If the user is asking about their expenses (e.g. "How much did I spend on coffee this month?"), output "Query".
- Otherwise, output "Others".

User input: {user_input}
"""
