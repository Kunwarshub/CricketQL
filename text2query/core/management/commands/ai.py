from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Cleans the Batting table or imports CSV"

    def generate_SQL(self, question: str):


        from django.conf import settings
        import groq



        client = groq.Client(api_key=settings.GROQ_API_KEY)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    'role':'system',
                    'content':'''You are an assistant that translates natural language queries into SQL queries. 
                                The database has 3 tables: 

                                core_batting(player_name, span, Mat, Inns, Runs, HS, Ave, BF, SR, Cent, half_Cent, duck, fours, sixes)
                                core_bowling(player_name, span, Mat, Inns, Overs, Runs, Wickets, Best, Ave, Econ, SR, 5w, 10w)
                                core_fielding(player_name, span, Mat, Inns, Dis, Ct, St, Ct_Wk, Ct_Fi, MD_total, MD_Ct, MD_St, DPI)

                                player_name is a string which is stored in the format ((initials last name) (country in uppercase)) (eg. V Kohli (INDIA), RG Sharma (INDIA), Shoaib Malik (ICC/PAK)), span is an integerrangefield (years), Mat and Inns are integers, and the rest are statistics.
                                Only generate SQL queries if the question is related to cricket statistics(we are using postgres, so use ILIKE where its valid).
                                If the question is not related to cricket, just say "please ask cricket related questions".
                                You only have to return the SQL query, no raw text, nothing, only the query required.
                                Always reference the table and column names exactly as given above.
                                Also only give the queries for those questions which can be accurately answered by the database itself, if the database cannot answer a question,
                                say "not in the data".
                                DO NOT return any Insert, delete, or update query at any cost.
                                If the user types full name use initials+last name for search, else stick to last name, dont forget to use '%' before and after the initials and before the last name as well, eg: %M% Hafeez%, %MS% Dhoni, etc.
                                Give the queries for all the 3 fields, ie, batting, bowling and fielding unless specified otherwise.
                                Always return the player_name with any other info as well
                                '''
                },

                {
                    'role':'user',
                    'content': question
                }
            ],
            model='openai/gpt-oss-120b'
        )

        query=chat_completion.choices[0].message.content

        return query
    
    def execute_SQL(self, query: str):
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            return results

    def handle(self, *args, **options):
        
        question = "What was the span of kunwar?"

        query = self.generate_SQL(question)
        if query == "please ask cricket related questions" or query == "not in the data":
            print(query)
        else:
            print(query)
            result = self.execute_SQL(query)
            if not len(result):
                print("not in data, please try with another name format")