from difflib import get_close_matches

PLAYER_NAME_MAP = {}  # empty at import time, populated at startup

FUZZY_STOPWORDS = {
    "names", "name", "players", "player", "top", "best", 
    "most", "runs", "wickets", "average", "list", "give",
    "show", "tell", "who", "what", "how", "many"
}

def load_player_names():
    from django.db import connection  # import here, not at top level
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT player_name FROM core_batting
            UNION
            SELECT DISTINCT player_name FROM core_bowling
            UNION
            SELECT DISTINCT player_name FROM core_fielding
        """)
        rows = cursor.fetchall()
    global PLAYER_NAME_MAP
    PLAYER_NAME_MAP = {row[0].lower(): row[0] for row in rows if row[0]}

def extract_player_name(query: str) -> str | None:
    query_lower = query.lower()
    query_words = [w for w in query_lower.split() if len(w) >= 4]
    
    print(f"query_words: {query_words}")  # what words are being checked

    best_score = 0
    best_match = None

    for normalized_name, original_name in PLAYER_NAME_MAP.items():
        name_only = normalized_name.split("(")[0].strip()
        name_parts = [p for p in name_only.split() if len(p) >= 4]

        if not name_parts:
            continue

        score = 0
        for q_word in query_words:
            matches = get_close_matches(q_word, name_parts, n=1, cutoff=0.9)
            if matches:
                score += 1
                print(f"MATCH: '{q_word}' matched '{matches}' in '{normalized_name}' score={score}")  # what's matching

        if score > best_score:
            best_score = score
            best_match = original_name

    return best_match if best_score >= 1 else None