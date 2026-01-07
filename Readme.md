# CricketQL 🏏

CricketQL is a Natural Language → SQL system that allows users to query a PostgreSQL database using plain English.

Unlike LLM-only systems, queries are executed against a real database with safety constraints and validation.

## Tech Stack
- Python
- Django
- PostgreSQL
- HTML / CSS / JavaScript
- LLMs (Groq + optional fallback)

## Features
- Natural language to SQL translation
- Safe SQL execution (read-only, validated)
- Graceful handling of ambiguous queries
- Optional fallback to external LLM when data is missing
- Clean, minimal UI

## Example Queries
- "Virat Kohli batting average in Tests"
- "Top 5 run scorers in ODIs since 2015"

## Setup
1. Clone the repo
2. Create a `.env` file with required API keys
3. Install dependencies:
   pip install -r requirements.txt
4. Run migrations and start server:
    python manage.py runserver

Disclaimer

This project uses demo/sample data. API keys and credentials are not included.