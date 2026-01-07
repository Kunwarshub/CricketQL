from django.conf import settings
import groq
from django.db import connection

def generate_SQL(question: str):

    client = groq.Client(api_key=settings.GROQ_API_KEY)  
    chat_completion = client.chat.completions.create(
        messages=[
            {
                'role':'system',
                'content':'''You are an assistant that translates natural language queries into SQL queries. 
                            The database has 3 tables:  
                            core_batting(player_name, span, Mat, Inns, Runs, HS, Ave, BF, SR, Cent, half_Cent, duck, fours, sixes)
                            core_bowling(player_name, span, Mat, Inns, Overs, Runs, Wkts, Ave, Econ, SR, fours, fives)
                            core_fielding(player_name, span, Mat, Inns, Dis, Ct, St, Ct_Wk, Ct_Fi, MD_total, MD_Ct, MD_St, DPI)  
                            player_name is a string which is stored in the format ((initials last name) (country in uppercase)) (eg. V Kohli (INDIA), RG Sharma (INDIA), Shoaib Malik (ICC/PAK)), span is an integerrangefield (years), Mat and Inns are integers, and the rest are statistics.
                            Only generate SQL queries if the question is related to cricket statistics(we are using postgres, so use ILIKE where its valid).
                            If the question is not related to cricket, just say "please ask cricket related questions".
                            You only have to return the SQL query, no raw text, nothing, only the query required.
                            Always reference the table and column names exactly as given above.
                            Also only give the queries for those questions which can be accurately answered by the database itself, if the database cannot answer a question,
                            say "not in the data" without returning any sql.
                            DO NOT return any Insert, delete, or update query at any cost.
                            If the user types full name use initials+last name for search, else stick to last name, dont forget to use '%' before and after the initials and before the last name as well, eg: %M% Hafeez%, %MS% Dhoni, etc.
                            Give the queries for all the 3 fields, ie, batting, bowling and fielding unless specified otherwise, then only give which is required.
                            Always return the player_name with any other info as well and quote column names.
                            The data is not yearwise, its the total stats of each player in their play span so whenever yearwise questions are asked, just say "not in the data".
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
    
def execute_SQL(query: str):
    with connection.cursor() as cursor:
        cursor.execute(query)
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