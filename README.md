# 🏦 Banking AI-Agent

An AI agentic pipeline for handling customer support issues in the banking domain. Built as part of **Lab 3 — Applications of Natural Language Processing in Industry** at the University of Science (VNUHCM).

## 🎯 Objective

This system receives a customer message, identifies the corresponding intent using a fine-tuned model, retrieves relevant policy information, generates a draft response, validates it, and determines whether the case can be handled automatically or should be escalated to human staff.

## 🏗️ Architecture

The system is a **monolith FastAPI backend** with a 6-node agentic pipeline:

```
Customer Message
       │
       ▼
┌──────────────────────────────────────────┐
│            FastAPI Backend               │
│                                          │
│  [1] Intent Node  ← ngbaoan/intent-banking (fine-tuned Qwen2.5-7B)
│       ↓                                  │
│  [2] Priority Node (rule-based)          │
│       ↓                                  │
│  [3] Policy Node (lookup)                │
│       ↓                                  │
│  [4] Draft Node   ← Ollama gpt-oss:20b  │
│       ↓                                  │
│  [5] Validation Node                     │
│       ↓                                  │
│  [6] Router Node → reply / ask / escalate│
└──────────────────────────────────────────┘
```

## 🧠 Models Used

| Component | Model | Source |
|---|---|---|
| Intent Detection | `ngbaoan/intent-banking` | [HuggingFace](https://huggingface.co/ngbaoan/intent-banking) — LoRA adapter on Qwen2.5-7B, fine-tuned on BANKING77 (77 intents, 92.29% accuracy) |
| Response Drafting | `gpt-oss:20b` | Ollama (local or via Google Colab + Pinggy tunnel) |

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- GPU recommended for intent model (6–8 GB VRAM for 4-bit inference), or runs on CPU (slower)
- Ollama running locally or via Google Colab + Pinggy

### 1. Start Ollama

**Option A — Local:**
```bash
ollama pull gpt-oss:20b
ollama serve
```

**Option B — Google Colab + Pinggy:**
Open `notebooks/Ollama-Pinggy.ipynb` on Colab, run all cells, and copy the Pinggy public URL. Then set it as `OLLAMA_BASE_URL` below.

### 2. Install & Run Backend

```bash
cd backend
pip install -r requirements.txt
# Set env vars if needed:
export OLLAMA_BASE_URL=http://localhost:11434   # or your Pinggy URL
export OLLAMA_MODEL=gpt-oss:20b
export INTENT_MODEL_NAME=ngbaoan/intent-banking
python run.py
```

Backend will be available at: http://localhost:8000  
Interactive API docs: http://localhost:8000/docs

### 3. (Optional) Run Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Frontend at: http://localhost:8501

### Running with Docker

```bash
# Set OLLAMA_BASE_URL in docker-compose.yml first
docker-compose up --build
```

## 📁 Project Structure

```
nlp_lab3/
├── docker-compose.yml
├── README.md
├── backend/                        # FastAPI backend + full agentic pipeline
│   ├── run.py                      # Entry point (uvicorn)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py                 # FastAPI app + /api/chat route
│   │   ├── core/
│   │   │   ├── settings.py         # Env config (Ollama URL, model name)
│   │   │   └── schemas.py          # Pydantic schemas for all node I/O
│   │   ├── data/
│   │   │   └── policies.py         # Dummy FAQ/policy data (13+ intents)
│   │   ├── clients/
│   │   │   ├── base.py             # Abstract LLM client interface
│   │   │   └── ollama_client.py    # Async HTTP client for Ollama
│   │   ├── nodes/
│   │   │   ├── intent_node.py      # Node 1: Intent Detection (fine-tuned model)
│   │   │   ├── priority_node.py    # Node 2: Priority/Risk Detection
│   │   │   ├── policy_node.py      # Node 3: Policy Retrieval
│   │   │   ├── draft_node.py       # Node 4: Response Drafting (LLM)
│   │   │   ├── validation_node.py  # Node 5: Response Validation
│   │   │   └── router_node.py      # Node 6: Routing/Escalation Decision
│   │   └── agent/
│   │       └── orchestrator.py     # Pipeline orchestrator (calls 6 nodes)
│   └── examples/
│       └── sample_requests.json    # 8 sample customer messages for testing
├── frontend/                       # Streamlit UI (optional, for demo)
│   └── app.py
├── intent_service/                 # Template for Lab 4 (gRPC microservice)
│   ├── intent_service.proto        # gRPC definition
│   ├── Makefile
│   └── ...
└── notebooks/
    └── Ollama-Pinggy.ipynb         # Run LLM on Google Colab
```

## 🧪 Testing

Use the provided sample requests to test the pipeline:

```bash
# Test with curl
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I tried to send money but the transfer failed."}'

# Or run the sample requests
python -c "
import requests, json
samples = json.load(open('backend/examples/sample_requests.json'))
for s in samples:
    r = requests.post('http://localhost:8000/api/chat', json={'message': s['message']})
    d = r.json()
    print(f'[{s[\"id\"]}] Intent: {d[\"trace\"][\"intent\"][\"intent\"]} | Action: {d[\"action\"]}')
"
```

## 🎬 Video Demo

> [Video demo link — to be added]

## 👤 Author

- **Nguyen Bao An** — University of Science, VNUHCM
- Lab 3 — Applications of NLP in Industry (2026)
