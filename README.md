# Banking AI-Agent (Microservices)

This is the Lab 3 implementation of the Banking AI-Agent, refactored into a microservice architecture using gRPC and Docker.

## Architecture
- **API Gateway (Backend)**: FastAPI (Port 8000)
- **Intent Service**: Python gRPC Microservice (Port 50051)
- **Frontend**: Streamlit (Port 8501)
- **LLM**: Ollama (gpt-oss:20b) running externally

## How to Run

1. **Set Ollama URL (e.g., from Pinggy):**
```bash
export OLLAMA_BASE_URL=https://<your-pinggy-id>.a.free.pinggy.link
```

2. **Build and Start with Docker Compose:**
```bash
docker compose up -d --build
```

3. **Access the Frontend:**
Open your browser and navigate to `http://localhost:8501`.

## Video Demonstration
[Insert link to your demo video here]
