import re

METRIC_MAP = {
    # ---------------- BATTING ----------------
    "runs": ("core_batting", "Runs"),
    "run": ("core_batting", "Runs"),
    "highest score": ("core_batting", "HS"),
    "hs": ("core_batting", "HS"),
    "average": ("core_batting", "Ave"),
    "avg": ("core_batting", "Ave"),
    "batting average": ("core_batting", "Ave"),
    "balls faced": ("core_batting", "BF"),
    "bf": ("core_batting", "BF"),
    "strike rate": ("core_batting", "SR"),
    "sr": ("core_batting", "SR"),
    "hundreds": ("core_batting", "Cent"),
    "centuries": ("core_batting", "Cent"),
    "100s": ("core_batting", "Cent"),
    "fifties": ("core_batting", "half_Cent"),
    "50s": ("core_batting", "half_Cent"),
    "ducks": ("core_batting", "duck"),
    "fours": ("core_batting", "fours"),
    "four": ("core_batting", "fours"),
    "4s": ("core_batting", "fours"),
    "sixes": ("core_batting", "sixes"),
    "six": ("core_batting", "sixes"),
    "6s": ("core_batting", "sixes"),
    "matches": ("core_batting", "Mat"),
    "mat": ("core_batting", "Mat"),
    "innings": ("core_batting", "Inns"),
    "inns": ("core_batting", "Inns"),
    
    # ---------------- BOWLING ----------------
    "overs": ("core_bowling", "Overs"),
    "maidens": ("core_bowling", "Mdns"),
    "mdns": ("core_bowling", "Mdns"),
    "wickets": ("core_bowling", "Wkts"),
    "wicket": ("core_bowling", "Wkts"),
    "wkts": ("core_bowling", "Wkts"),
    "best bowling": ("core_bowling", "BBI"),
    "bbi": ("core_bowling", "BBI"),
    "bowling average": ("core_bowling", "Ave"),
    "economy": ("core_bowling", "Econ"),
    "econ": ("core_bowling", "Econ"),
    "bowling strike rate": ("core_bowling", "SR"),
    "four wickets": ("core_bowling", "fours"),
    "4 wickets": ("core_bowling", "fours"),
    "five wickets": ("core_bowling", "fives"),
    "5 wickets": ("core_bowling", "fives"),

    # ---------------- FIELDING ----------------
    "dismissals": ("core_fielding", "Dis"),
    "dis": ("core_fielding", "Dis"),
    "catches": ("core_fielding", "Ct"),
    "catch": ("core_fielding", "Ct"),
    "stumpings": ("core_fielding", "St"),
    "stumping": ("core_fielding", "St"),
    "keeping catches": ("core_fielding", "Ct_Wk"),
    "field catches": ("core_fielding", "Ct_Fi"),
    "dismissals per innings": ("core_fielding", "DPI"),
    "dpi": ("core_fielding", "DPI"),
}

TABLE_HINTS = {
    "core_batting": ["batting", "batsman", "batter"],
    "core_bowling": ["bowling", "bowler"],
    "core_fielding": ["fielding", "keeper", "wicketkeeping"],
}

AMBIGUOUS_METRICS = {"Runs", "Ave", "SR", "span"}

ALIASES = sorted(METRIC_MAP.keys(), key=len, reverse=True)

def resolve_table(metric, normalized_question):
    # 1. Explicit hints based on the question context
    for table, hints in TABLE_HINTS.items():
        for hint in hints:
            if hint in normalized_question:
                return table

    # 2. Ambiguity fallback: If the metric is ambiguous, return a default table (e.g., "core_batting")
    if metric in AMBIGUOUS_METRICS:
        return "core_batting"

    return None

def extract_metric(normalized_question: str):
    for alias in ALIASES:
        pattern = r"\b" + re.escape(alias) + r"\b"  # Ensure we're matching whole words

        if re.search(pattern, normalized_question):
            table, metric = METRIC_MAP[alias]

            # Remove the alias from the question and clean up extra spaces
            remaining = re.sub(pattern, "", normalized_question, count=1)
            remaining = " ".join(remaining.split())

            # If metric is ambiguous, try resolving it with context
            if metric in AMBIGUOUS_METRICS:
                resolved_table = resolve_table(metric, normalized_question)
                if resolved_table:
                    table = resolved_table

            return table, metric, remaining

    return None, None, normalized_question

# Main code
question = "runs by kohli"
normalized_question = " ".join(re.sub(r"[^a-z0-9\s]", " ", question.lower()).split())

# Print the result
print(extract_metric(normalized_question))