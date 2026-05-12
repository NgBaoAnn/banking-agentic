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

- Docker and Docker Compose installed.
- A Google account to run the Colab notebooks for the models.

### 1. Start External Models via Google Colab
Since the models require GPU resources, they are hosted on Google Colab and exposed via Pinggy tunnels.
1. Open `notebooks/Intent-Service-Colab.ipynb` on Colab, run all cells, and copy the generated Pinggy URL.
2. Open `notebooks/Ollama-Pinggy.ipynb` on Colab, run all cells, and copy the generated Pinggy URL.

### 2. Configure Environment Variables
Open the `docker-compose.yml` file and replace the placeholder URLs with the Pinggy URLs you obtained from the Colab notebooks:
```yaml
    environment:
      # Node 1: Intent Classification Service
      INTENT_SERVICE_URL: http://<your-intent-pinggy-url>.run.pinggy-free.link
      INTENT_MODEL_NAME: ngbaoan/intent-banking

      # Node 4: Ollama LLM
      OLLAMA_BASE_URL: http://<your-ollama-pinggy-url>.run.pinggy-free.link
      OLLAMA_MODEL: gpt-oss:20b
```

### 3. Run with Docker Compose
Build and run the entire application (Backend + Frontend) using Docker Compose:
```bash
docker-compose up --build
```

### 4. Access the Application
- **Frontend (Streamlit Chat UI):** http://localhost:8501
- **Backend API:** http://localhost:8000
- **Interactive API docs:** http://localhost:8000/docs

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

[Watch the Video Demo on Google Drive](https://drive.google.com/file/d/1oCl5iN5XTgb5VEvlFfI7MpyHn9EpEK9i/view?usp=drive_link)

## Author

- Nguyen Bao An - University of Science, VNUHCM
- Lab 3 - Applications of NLP in Industry (2026)
