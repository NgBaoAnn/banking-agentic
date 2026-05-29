# Banking AI-Agent (Microservices)

This is the Lab 3 implementation of the Banking AI-Agent, refactored into a microservice architecture using gRPC and Docker.

## Architecture

```mermaid
graph TD
    subgraph "Docker Compose Environment"
        F[💻 Frontend<br/>(Streamlit - :8501)]
        G[⚙️ API Gateway<br/>(FastAPI - :8000)]
        I[🧠 Intent Service<br/>(gRPC - :50051)]
    end
    
    O[☁️ External LLM<br/>(Ollama via Pinggy)]
    U((👤 User))
    
    U -->|Interacts| F
    F -->|HTTP POST /run-agent| G
    G -->|gRPC Request| I
    I -->|HTTP POST<br/>(Classify Intent)| O
    G -->|HTTP POST<br/>(Generate Draft)| O
    
    classDef frontend fill:#E34F26,stroke:#333,stroke-width:2px,color:#fff;
    classDef gateway fill:#008080,stroke:#333,stroke-width:2px,color:#fff;
    classDef grpc fill:#2E8B57,stroke:#333,stroke-width:2px,color:#fff;
    classDef external fill:#8A2BE2,stroke:#333,stroke-width:2px,color:#fff;
    classDef user fill:#666,stroke:#333,stroke-width:2px,color:#fff;
    classDef box fill:#f9f9f9,stroke:#666,stroke-width:1px,stroke-dasharray: 5 5;
    
    class F frontend;
    class G gateway;
    class I grpc;
    class O external;
    class U user;
```

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
