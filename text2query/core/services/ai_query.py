from django.conf import settings
import groq
from django.db import connection

def generate_SQL(question: str):

    client = groq.Client(api_key=settings.GROQ_API_KEY)  
    chat_completion = client.chat.completions.create(
        messages=[
            {
                'role':'system',
                'content':'''You are a system that converts cricket statistics questions into PostgreSQL SQL queries.

                            DATABASE SCHEMA:

                            Tables:

                            core_batting(
                                player_name,
                                span,
                                Mat,
                                Inns,
                                Runs,
                                HS,
                                Ave,
                                BF,
                                SR,
                                Cent,
                                half_Cent,
                                duck,
                                fours,
                                sixes
                            )

                            core_bowling(
                                player_name,
                                span,
                                Mat,
                                Inns,
                                Overs,
                                Runs,
                                Wkts,
                                Ave,
                                Econ,
                                SR,
                                fours,
                                fives
                            )

                            core_fielding(
                                player_name,
                                span,
                                Mat,
                                Inns,
                                Dis,
                                Ct,
                                St,
                                Ct_Wk,
                                Ct_Fi,
                                MD_total,
                                MD_Ct,
                                MD_St,
                                DPI
                            )

                            IMPORTANT RULES:

                            1. player_name values are stored as:
                               "<INITIALS> <LASTNAME> (COUNTRY)"
                               Example: "V Kohli (INDIA)", "MS Dhoni (INDIA)".

                            2. NEVER hardcode player names in SQL.
                               Always use a parameter placeholder:

                                   player_name ILIKE %s

                               The application will provide the value.

                            3. Only generate SELECT queries.
                               NEVER generate INSERT, UPDATE, DELETE, ALTER, or DROP queries.

                            4. Use column names EXACTLY as defined (CASE SENSITIVE).

                            5. Use PostgreSQL syntax and ILIKE for text matching when needed.

                            6. Statistics represent total career data only.
                               If a question asks for year-wise or time-filtered data, respond exactly:

                                   not in the data

                            7. If a question is unrelated to cricket statistics, respond exactly:

                                   please ask cricket related questions

                            8. If the database cannot answer the question using the available schema, respond exactly:

                                   not in the data

                            9. PostgreSQL is case-sensitive for identifiers.

                                ALL table names and column names MUST ALWAYS be wrapped in double quotes.
                                
                                Examples:
                                
                                Correct:
                                SELECT "Runs" FROM "core_batting"
                                WHERE "player_name" ILIKE %s;
                                
                                Incorrect:
                                SELECT Runs FROM core_batting
                                SELECT runs FROM core_batting
                                
                                Always preserve the exact column casing by using double quotes.

                            OUTPUT FORMAT:

                            Return ONLY the SQL query or one of the allowed fallback responses.
                            Do NOT include explanations or extra text.
                            '''
            },   
            {
                'role':'user',
                'content': question
            }
        ],
        model='openai/gpt-oss-120b'
        )

    query=chat_completion.choices[0].message.content.strip() 
    
    return query    
    
def execute_SQL(query: str, player_name):
    with connection.cursor() as cursor:
        cursor.execute(query, [player_name])
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
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