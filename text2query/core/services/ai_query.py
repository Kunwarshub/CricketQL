from django.conf import settings
import groq
from django.db import connection

SCHEMAS = {
    "core_batting": '("player_name", "span", "Mat", "Inns", "Runs", "HS", "Ave", "BF", "SR", "Cent", "half_Cent", "duck", "fours", "sixes")',
    "core_bowling": '("player_name", "span", "Mat", "Inns", "Overs", "Mdns", "Runs", "Wkts", "BBI", "Ave", "Econ", "SR", "fours", "fives")',
    "core_fielding": '("player_name", "span", "Mat", "Inns", "Dis", "Ct", "St", "Ct_Wk", "Ct_Fi", "MD_total", "MD_Ct", "MD_St", "DPI")',
}

def generate_SQL(table, metric, question):
    client = groq.Client(api_key=settings.GROQ_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                'role': 'system',
                'content': f'''You are a system that converts cricket statistics questions into PostgreSQL SQL queries.

                            Use these extracted details as guidance:
                            - Table: "{table}"
                            - Column: "{metric}"
                            - Schema: {SCHEMAS[table]}

                            IMPORTANT RULES:
                            - Wrap ALL identifiers in double quotes
                            - Always append NULLS LAST to ORDER BY
                            - NEVER hardcode player names, use ILIKE %s if needed
                            - Return ONLY the SQL, nothing else
                            - "span" is an IntegerRangeField, NEVER filter on it
                            - If the question asks about a specific year or tournament like IPL, respond exactly: not in the data

                            DATABASE CONTEXT:
                            - This database contains ONLY T20 World Cup career statistics (total/aggregate, not year-wise)
                            - If the question mentions a specific year (e.g. 2019, 2020), respond exactly: not in the data
                            - If the question mentions IPL, BBL, PSL or any non-T20 World Cup tournament, respond exactly: not in the data
                            - If the question asks about T20 World Cup stats without a specific year, answer normally
                            - If the question asks general T20 stats without mentioning a year, answer normally
                            '''
            },
            {
                'role': 'user',
                'content': question
            }
        ],
        model='openai/gpt-oss-120b'
    )
    return chat_completion.choices[0].message.content.strip()   


def build_sql(table, metric, has_player, question):
    if has_player:
        sql = f'SELECT "player_name", "{metric}" FROM "{table}" WHERE "player_name" ILIKE %s'
        return sql, False
    else:
        sql = generate_SQL(table, metric, question)
        return sql, True
    
    
def execute_SQL(query: str, player_name):
    with connection.cursor() as cursor:
        params = [f"%{player_name}%"] if player_name else []
        if "%s" in query and not params:
            return [], []  # SQL expects a param but none was extracted
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description] if cursor.description else []
        return rows, columns
    
def fallback_to_LLM(question: str):
    client = groq.Client(api_key=settings.FALLBACK_API_KEY)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system",
             "content": "You are a general cricket knowledge assistant, give concise, one line answers to the quesions asked."},
            {"role": "user",
             "content": question}
        ],
        model="openai/gpt-oss-120b"
    )
    result = chat_completion.choices[0].message.content.strip()
    return result