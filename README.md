# Expense Manager WhatsApp Bot

## Overview
This is a WhatsApp bot that allows users to record their expenses and query past expenses using natural language. The bot uses AI to classify user intent, extract structured expense data, and retrieve relevant expense records for queries. It is built using Flask, LangGraph, LangChain, and Twilio for WhatsApp integration.

## DEMO LINK: https://drive.google.com/file/d/1STKI9QnmyfZuPuR5EJHfQD-N1v6GW-fw/view?usp=sharing

## Features
- **Record Expenses**: Users can enter expenses in natural language (e.g., *"Spent 200 on lunch today"*).
- **Query Expenses**: Users can ask questions like *"How much did I spend on coffee this month?"*.
- **AI-Powered Parsing**: Uses LLMs to extract structured data from user inputs.
- **Persistent State Management**: Stores session history to maintain continuity.
- **Formatted Responses**: Outputs well-structured and human-readable responses.

## Project Structure
```
├── app.py              # Main Flask app handling WhatsApp interactions
├── classes.py          # Data models for expenses and app state
├── prompts.py          # Prompt templates for LLM interactions
├── requirements.txt    # Required dependencies
├── state_db.pkl        # Persistent session history
├── tempfile.json       # Temporary storage for expense queries
├── my_graph.png        # Visual representation of the AI workflow
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Twilio Account for WhatsApp integration
- Groq API Key for LLM interaction

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Aditya0105singh/expense-manager-whatsapp-bot
   cd expense-manager-whatsapp-bot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your Twilio and Groq API credentials:
   ```ini
   GROQ_API_KEY=your_groq_api_key
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## How It Works
1. **User sends a message on WhatsApp** → The bot processes the message.
2. **Intent Classification** → Determines if the message is about recording or querying expenses.
3. **Expense Parsing** → Extracts structured data from user input (if it's an expense entry).
4. **Query Processing** → Filters expenses and returns relevant results.
5. **Response Generation** → Returns a structured and formatted WhatsApp message.

## API Endpoints
### `POST /`
- **Request**: Twilio sends user messages to this endpoint.
- **Response**: A WhatsApp message is sent back based on the processed intent.

## AI Workflow (LangGraph)

![image](my_graph.png)

The AI workflow consists of the following nodes:
- **Intent Classification** → Identifies whether the user input is an expense, query, or other.
- **Parse Expense** → Extracts structured data when an expense is recorded.
- **Query Expenses** → Retrieves relevant expenses when queried.
- **Final Response** → Generates a WhatsApp-friendly message based on the intent.

A visual representation of the graph is stored in `my_graph.png`.

## Example Messages

### Recording Expenses
User: *"Spent 300 on groceries and 150 on snacks today."*

Bot Response:
```
Hi! The following expenses have been successfully recorded:
- *Groceries* for *₹300* on *2025-02-09*
- *Snacks* for *₹150* on *2025-02-09*
Thank you!
```

### Querying Expenses
User: *"How much did I spend last week?"*

Bot Response:
```
Based on your inquiry, here is the information you requested:
- Total expenses for *last week*: *₹3,250*
If you need further details, feel free to ask!
```
