import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .services.ai_query import generate_SQL, execute_SQL, fallback_to_LLM
from django.shortcuts import render
from psycopg2.extras import NumericRange

def landing(request):
    return render(request, "core/landing.html")

def home(request):
    return render(request, "core/index.html")

def span_to_JSON(columns, row):
    obj = {}
    for cols, value in zip(columns, row):
        if (isinstance(value, NumericRange)):
            obj[cols] = {
                "start":value.lower,
                "end": value.upper,
                "start_inclusive": value.lower_inc,
                "end_inclusive": value.upper_inc
            }
        else:
            obj[cols] = value
    return obj

@csrf_exempt
def api_query(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    question = body.get("question")
    use_fallback = body.get("use_fallback", False)
    if not question:
        return JsonResponse({"error": "No question provided"}, status=400)

    sql = generate_SQL(question)
    print (sql)

    # AI guardrails
    if sql in ("please ask cricket related questions"):
        return JsonResponse({
            "sql": None,
            "message": sql
        })
    
    #Fallback
    if sql in ("not in the data"):
        if (use_fallback):
            result = fallback_to_LLM(question)
            return JsonResponse({
                "sql": "No SQL generated",
                "result" : result + "\n\nNOTE: This answer is not sourced from the database but from an external LLM"
            })
        else: return JsonResponse({
            "sql": None,
            "message": sql
        })

    # Safety check
    if not sql.lower().startswith("select"):
        return JsonResponse({
            "sql": sql,
            "error": "Only SELECT queries are allowed"
        }, status=400)

    try:
        rows, columns = execute_SQL(sql)

        result = [span_to_JSON(columns, row) for row in rows]

        if not result:
            return JsonResponse({
                "sql": sql,
                "message": "No data found"
            })


        return JsonResponse({
            "sql": sql,
            "result": result
        })

    except Exception as e:
        return JsonResponse({
            "sql": sql,
            "error": str(e)
        }, status=500)

