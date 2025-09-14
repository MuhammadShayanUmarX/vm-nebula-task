

pip install -r requirements.txt
python app.py

Server runs on http://localhost:8000

# How it works

The system has 3 agents that automatically detect query types:
- Code assistant (triggered by programming keywords)
- Research assistant (for analysis and comparison)
- Task helper (for step-by-step guides)

Routes queries to appropriate models:
- Simple queries go to fast models
- Complex queries use premium models
- Automatic fallback if primary model fails

# API endpoints

# Regular chat
curl -X POST http://localhost:8000/chat -d '{"query":"What is Python?"}' -H "Content-Type: application/json"

# Streaming chat
curl -X POST http://localhost:8000/chat/stream -d '{"query":"Explain AI"}' -H "Content-Type: application/json"

# Health check
curl http://localhost:8000/health
`

# Setup
Create a .env file with your API keys:
```
GEMINI_API_KEY=your_key
Z_API_KEY=your_key
```


# Files

- app.py - main application
- config.py - model configuration
- requirements.txt - dependencies
- sessions.db - chat history (auto-created)
