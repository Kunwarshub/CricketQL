import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .services.ai_query import generate_SQL, execute_SQL, fallback_to_LLM
from .services.redis_check import get_cache, set_cache, redis_available
from .services.metric_normalization import extract_metric
from .services.extract_names import build_player_pattern
from django.shortcuts import render
from psycopg2.extras import NumericRange
import re

INVALID_SQL = {
    "not in the data",
    "please ask cricket related questions",
    None,
    ""
}


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
    
    #Normalize Question
    normalized_question = " ".join(re.sub(r"[^a-z0-9\s]", " ", question.lower()).split())

    table, metric, remaining = extract_metric(normalized_question)

    player_name = build_player_pattern(remaining)
    print(player_name)

    key = json.dumps((table, metric), separators=(",", ":"))

    sql = get_cache(key)

    generated_new_SQL = False

    #If not in redis cache
    if not sql:
        sql = generate_SQL(normalized_question)
        generated_new_SQL = True
        print(sql)

    # AI guardrails
    if sql == "please ask cricket related questions":
        return JsonResponse({
            "sql": None,
            "message": sql
        })
    
    #Fallback
    if sql == "not in the data":
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
        rows, columns = execute_SQL(sql, player_name)

        result = [span_to_JSON(columns, row) for row in rows]

        if not result:
            return JsonResponse({
                "sql": sql,
                "message": "No data found"
            })
        
        if redis_available and sql not in INVALID_SQL and generated_new_SQL:
            set_cache(key, sql)
            print("Cached: ", key)


        return JsonResponse({
            "sql": sql,
            "result": result
        })

    except Exception as e:
        return JsonResponse({
            "sql": sql,
            "error": str(e)
        }, status=500)

