# 🏏 CricketQL

**CricketQL** is a **Natural Language → SQL** system that lets users query T20 World Cup cricket statistics using plain English.

Unlike LLM-only chat systems, CricketQL executes queries against a **real PostgreSQL database** with validation, safety guardrails, and intelligent caching — ensuring **accurate, deterministic results** instead of hallucinated answers.

---

## 🧠 Architecture Overview

```
User Query
     ↓
Normalization + Feature Extraction (metric + table + player name)
     ↓
     ├── Player detected → SQL built in Python instantly (no LLM call)
     │
     └── No player → Redis cache check
                          ↓
                    Cache hit  → reuse cached SQL template
                          ↓
                    Cache miss → LLM generates SQL → cached for future use
     ↓
Validation Layer (SELECT-only enforcement, guardrails)
     ↓
PostgreSQL execution → structured results returned
```

The key insight: since metric and table are already extracted from the query, player-specific SQL can be built deterministically in Python — the LLM is only called when genuinely needed for complex ranking or aggregation queries, and its output is cached in Redis so subsequent similar queries never hit the LLM again.

---

## 🔄 Query Flow

1. User submits a natural language question
2. Query is normalized — metric, table, and player name extracted using dictionary matching and fuzzy name resolution against the actual database
3. If player detected → SQL built instantly in Python using extracted features, zero LLM calls
4. If no player → Redis cache checked using `(table, metric)` as key
5. Cache miss → LLM generates SQL with table/schema context injected → result cached
6. SQL validated (SELECT-only enforcement)
7. PostgreSQL executes query, structured JSON returned to UI
8. If no data found and fallback enabled → external LLM answers from general knowledge with a clear disclaimer

---

## ✨ Features

- Natural language → SQL translation scoped to T20 World Cup statistics
- Feature extraction pipeline — metric, table, and player name resolved before LLM is involved
- Fuzzy player name matching against live database records — handles nicknames and partial names
- Redis-based SQL template caching — LLM only called on genuinely new query types
- Python SQL builder for player queries — deterministic, fast, free
- Safe SQL execution — read-only SELECT enforcement
- Schema-aware LLM prompting — table name, column name, and schema injected per query
- Graceful handling of unsupported queries (year-specific, IPL, non-cricket)
- Optional fallback LLM for queries outside the database scope
- Containerized multi-service architecture via Docker Compose

---

## 💬 Example Queries

| Query | Behaviour |
|-------|-----------|
| `Virat Kohli batting average` | Template SQL, player filter |
| `Top 10 players by runs` | LLM generated SQL, cached |
| `Malinga bowling economy` | Template SQL, player filter |
| `Most wickets in T20 World Cup` | LLM generated SQL, cached |
| `Dhoni dismissals per innings` | Template SQL, player filter |
| `Kohli runs in 2019` | Returns: not in the data |
| `IPL top scorers` | Returns: not in the data |

---

## ⚙️ Tech Stack

- **Backend** — Python, Django
- **Database** — PostgreSQL
- **Caching** — Redis
- **LLM** — Groq API
- **Frontend** — HTML / CSS / JavaScript
- **Infrastructure** — Docker, Docker Compose

---

## 🚀 One-Command Setup (Recommended)

```bash
docker compose up
```

This automatically starts:

- Django API server
- PostgreSQL database
- Redis caching layer
- Database migrations
- Automatic dataset loading

No manual installation of Python, PostgreSQL, or Redis required.

Open in browser: `http://localhost:8000`

---

## 🛠 Manual Setup

**1. Clone the repository**
```bash
git clone <repo-url>
cd cricketql
```

**2. Create a `.env` file**
```
PRIMARY_API_KEY=your_groq_api_key
FALLBACK_API_KEY=your_fallback_api_key
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure PostgreSQL**

Update database credentials in `settings.py`.

**5. Start Redis**
```bash
docker run -d -p 6379:6379 redis
```

**6. Run migrations**
```bash
python manage.py migrate
```

**7. Load dataset**
```bash
python manage.py load_data
```

**8. Start server**
```bash
python manage.py runserver
```

---

## ⚠️ Known Limitations

- **No year-wise data** — database contains T20 World Cup career totals only. Year-specific or tournament-specific queries (IPL, BBL, PSL) are explicitly rejected.
- **Player name spelling** — fuzzy matching uses a 0.9 similarity threshold. Significant typos may not resolve correctly, by design, to prevent false positive matches against common English words.
- **Single metric queries only** — cross-table queries (e.g. all-rounder rankings combining batting + bowling stats) are not yet supported.
- **T20 World Cup scope only** — general cricket questions outside this dataset are handled by the optional fallback LLM with a clear disclaimer.

---

## Project Preview

![App Screenshot 1](text2query/data/SS1.png)
![App Screenshot 2](text2query/data/SS2.png)

---

> ⚠️ This project uses demo cricket statistics data for educational purposes. API keys and credentials are not included.