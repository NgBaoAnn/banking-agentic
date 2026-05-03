# Banking AI-Agent

An AI agentic pipeline for handling customer support issues in the banking domain. Built as part of Lab 3 - Applications of Natural Language Processing in Industry at the University of Science (VNUHCM).

## Objective

This system receives a customer message, identifies the corresponding intent using a fine-tuned model, retrieves relevant policy information, generates a draft response, validates it, and determines whether the case can be handled automatically or should be escalated to human staff.

## Architecture

The system is a monolith FastAPI backend with a 6-node agentic pipeline:

```
Customer Message
       |
       v
------------------------------------------
            FastAPI Backend               
                                          
  [1] Intent Node  <- ngbaoan/intent-banking (fine-tuned Qwen2.5-7B)
       |                                  
  [2] Priority Node (rule-based)          
       |                                  
  [3] Policy Node (lookup)                
       |                                  
  [4] Draft Node   <- Ollama gpt-oss:20b  
       |                                  
  [5] Validation Node                     
       |                                  
  [6] Router Node -> reply / ask / escalate
------------------------------------------
```

## Models Used

| Component | Model | Source |
|---|---|---|
| Intent Detection | ngbaoan/intent-banking | HuggingFace - LoRA adapter on Qwen2.5-7B, fine-tuned on BANKING77 |
| Response Drafting | gpt-oss:20b | Ollama (local or via Google Colab + Pinggy tunnel) |

## Getting Started

### Prerequisites

- Python 3.10+
- GPU recommended for intent model (6-8 GB VRAM for 4-bit inference), or runs on CPU
- Ollama running locally or via Google Colab + Pinggy

### 1. Start Ollama

Option A - Local:
```bash
ollama pull gpt-oss:20b
ollama serve
```

Option B - Google Colab + Pinggy:
Open notebooks/Ollama-Pinggy.ipynb on Colab, run all cells, and copy the Pinggy public URL. Then set it as OLLAMA_BASE_URL below.

### 2. Install & Run Backend

```bash
cd backend
pip install -r requirements.txt
export OLLAMA_BASE_URL=http://localhost:11434
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
docker-compose up --build
```

## Project Structure

```
nlp_lab3/
|-- docker-compose.yml
|-- README.md
|-- backend/
|   |-- run.py
|   |-- requirements.txt
|   |-- Dockerfile
|   |-- app/
|   |   |-- main.py
|   |   |-- core/
|   |   |-- data/
|   |   |-- clients/
|   |   |-- nodes/
|   |   `-- agent/
|   `-- examples/
|-- frontend/
`-- notebooks/
```

## Testing

Use the provided sample requests to test the pipeline:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I tried to send money but the transfer failed."}'
```

## Video Demo

[Video demo link - to be added]

## Author

- Nguyen Bao An - University of Science, VNUHCM
- Lab 3 - Applications of NLP in Industry (2026)
