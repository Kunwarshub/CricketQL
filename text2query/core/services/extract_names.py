NON_NAME_WORDS = {
    "by", "of", "the", "is", "did", "does",
    "how", "many", "what", "tell", "me",
    "show", "give", "taken", "score",
    "stats", "player", "players", "were", "the", "total", "scored"
}

def extract_name_tokens(remaining):
    words = remaining.lower().split()

    tokens = [
        w for w in words
        if w not in NON_NAME_WORDS and w.isalpha()
    ]

    return tokens

def build_player_pattern(remaining):

    tokens = extract_name_tokens(remaining)

    if not tokens:
        return None

    # single token → surname search
    if len(tokens) == 1:
        return f"%{tokens[0].capitalize()}%"

    # multi token → initials + surname
    lastname = tokens[-1].capitalize()
    initials = "".join(t[0].upper() for t in tokens[:-1])

    return f"%{initials}% {lastname}%"