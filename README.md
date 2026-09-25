# Scalable API Async AI System

A Django-based backend that wraps a **ReAct AI agent** in a production-style, **asynchronous, horizontally-scalable API**. Slow LLM/tool calls are offloaded to Celery workers instead of blocking the request cycle, with Redis as the broker/cache, Docker for deployment, and Locust for load testing.

## Features

- **ReAct-style AI agent** (LangChain `create_agent`, Ollama Cloud model) with three tools:
  - `search` — web search via Tavily
  - `calc` — safe arithmetic evaluation
  - `db_query` — read-only `SELECT` queries against a sample customer database
- **Persistent conversation memory** — every user/assistant turn is stored per `session_id` in a SQLite database via SQLAlchemy, so history survives server restarts
- **Async task processing** — API requests return immediately (`202 Accepted` + `task_id`); the actual agent/LLM call runs in a Celery worker, decoupling slow inference from the web process
- **Automatic retries** — Celery tasks retry failed agent runs with exponential backoff
- **Token & cost tracking** — usage metadata from every agent step is aggregated to report input/output/total tokens and estimated cost per request
- **Rate limiting** — custom Django middleware capping requests per IP (60/min), backed by Redis cache
- **Health check endpoint** for load balancers / orchestrators
- **OpenAPI docs** via `drf-spectacular` (Swagger UI)
- **Containerized deployment** — `Dockerfile` + `docker-compose.yml` wiring `web` (Django/Gunicorn), `worker` (Celery), and `redis`
- **Load testing** with Locust to validate the async pattern holds up under concurrent traffic

## Architecture

```
Client (Postman / Locust)
        │
        ▼
Django REST API  ──►  Rate limit middleware  ──►  202 Accepted + task_id
        │
        ▼
   Celery task queue (Redis broker)
        │
        ▼
   Celery worker
        │
        ├── ReAct Agent (LangChain + Ollama Cloud)
        │     ├── search tool
        │     ├── calc tool
        │     └── db_query tool  ──►  SQLite (business.db)
        │
        └── Conversation memory  ──►  SQLite (memory.db)
        │
        ▼
Client polls GET /api/tasks/<task_id>/  ──►  result + token usage
```

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | Django, Django REST Framework |
| Agent framework | LangChain (`create_agent`) |
| LLM | Ollama Cloud (`gpt-oss:120b-cloud`) |
| Task queue | Celery |
| Broker / cache | Redis |
| Memory store | SQLite + SQLAlchemy |
| API docs | drf-spectacular |
| Load testing | Locust |
| Deployment | Docker, docker-compose |

## Project Structure

```
.
├── agent_app/              # Agent, tools, memory, API views
│   ├── agent.py
│   ├── tools.py
│   ├── memory.py
│   └── urls.py
├── config/                 # Django project settings
├── create_database.py      # Seeds sample business.db (customers table)
├── locustfile.py           # Load test scenarios
├── docker-compose.yml      # web + worker + redis services
├── Dockerfile
├── requirements.txt
└── manage.py
```

## Getting Started

### Prerequisites

- Python 3.12
- Redis
- An Ollama Cloud API key (or a local Ollama instance)

### Local Setup

```bash
# clone and enter the project
git clone https://github.com/albinea/scalable-api-async-ai-system.git
cd scalable-api-async-ai-system

# create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# configure environment variables
cp .env.example .env   # add your OLLAMA_API_KEY, etc.

# seed the sample database
python create_database.py

# apply Django migrations
python manage.py migrate

# start Redis (if not already running)
redis-server

# start the Celery worker (separate terminal)
celery -A config worker --loglevel=info

# start the Django dev server
python manage.py runserver
```

### Running with Docker

```bash
docker-compose up --build
```

This starts the `web`, `worker`, and `redis` services together.

## API Usage

### Send a chat message

```
POST /api/chat/
Content-Type: application/json

{
  "session_id": "user-123",
  "message": "How many customers are from Kochi?"
}
```

Response:

```json
{
  "task_id": "a1b2c3d4-...",
  "status": "processing"
}
```

### Poll for the result

```
GET /api/tasks/<task_id>/
```

Response (once complete):

```json
{
  "status": "completed",
  "result": "There are 12 customers from Kochi.",
  "usage": {
    "input_tokens": 512,
    "output_tokens": 48,
    "total_tokens": 560,
    "estimated_cost_usd": 0.0021
  }
}
```

### Health check

```
GET /api/health/
```

### API Documentation

Interactive Swagger UI is available at:

```
GET /api/docs/
```

## Load Testing

Simulate concurrent traffic with Locust:

```bash
locust -f locustfile.py --host=http://localhost:8000
```

Then open `http://localhost:8089` to configure and run a swarm (e.g., 20 users over 5 minutes) and confirm the API responds with `202` under load rather than timing out.

## Observability

For deeper visibility into agent tool calls, retries, and latency, consider integrating [LangSmith](https://www.langchain.com/langsmith) tracing instead of relying on manual logging.

## License

Add your license of choice here.
