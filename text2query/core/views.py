from django.http import StreamingHttpResponse, JsonResponse
from .tools.agent import get_agent
import json, logging
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import hashlib
from .services.redis_check import set_cache, get_cache, get_redis

logger = logging.getLogger(__name__)

def chat(request):
    return render(request, 'chat.html')

def clear_session(request):
    request.session.flush()  # destroys and recreates session key
    return JsonResponse({"status": "ok"})

def create_key(user_msg):
    msg_normalized = user_msg.lower().strip()
    hashed = hashlib.md5(msg_normalized.encode()).hexdigest()
    return hashed

@csrf_exempt
def get_result(request):

    import time

    start = time.time()

    logger.info("redis status", extra={"redis_available": get_redis() is not None})
    if request.method == "POST":

        agent = get_agent()
        body = json.loads(request.body)
        user_msg = body.get("message")
        session_id = request.session.session_key

        config = {"configurable" : {"thread_id": session_id}}

        cache_key = create_key(user_msg)
        cached = get_cache(cache_key)
        if cached is not None:
            return JsonResponse({
                "response": cached
            })    

        def stream():


            input_tokens = 0
            output_tokens = 0
            full_response = []
            
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": user_msg}]},
                config=config,
                stream_mode="messages"
            ):
                message,metadata = chunk

                if metadata.get("langgraph_node") == "tools":
                    yield f"data: {json.dumps({'status': 'Querying database...'})}\n\n"

                if hasattr(message, "usage_metadata") and message.usage_metadata:
                    input_tokens = message.usage_metadata.get('input_tokens', 0)
                    output_tokens = message.usage_metadata.get('output_tokens', 0)

                if hasattr(message, 'content') and message.content:
                    if metadata.get("langgraph_node") == "model":
                        full_response.append(message.content)
                        yield f"data: {json.dumps({'token': message.content})}\n\n"

            set_cache(cache_key, "".join(full_response) )
            duration_ms = int((time.time()-start)*1000)
            logger.info("stream completed", extra={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "session_id": session_id,
                "duration_ms": duration_ms,
                "user_msg": user_msg,
                "md5": cache_key,
            })        
            yield "data: [DONE]\n\n"

        return StreamingHttpResponse(stream(), content_type="text/event-stream")