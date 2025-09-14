

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
  
# ScreenShots
<img width="1510" height="669" alt="swagger chat 1 question" src="https://github.com/user-attachments/assets/96684cce-f077-4d5e-aa66-aec9b2181c47" />
<img width="1275" height="652" alt="swagger chat 1 response" src="https://github.com/user-attachments/assets/55e35375-b281-4e22-9038-24b293b982b4" />
<img width="1445" height="596" alt="swagger model status execution" src="https://github.com/user-attachments/assets/717f51a5-ffe4-401a-b0d9-01881b8af789" />
<img width="1262" height="538" alt="swagger model status response" src="https://github.com/user-attachments/assets/7753aad4-bb6d-417a-838f-820f3bee993f" />
<img width="740" height="555" alt="streaming results" src="https://github.com/user-attachments/assets/096c64ca-b920-4e0d-b365-0e67454f80a0" />
<img width="1336" height="650" alt="Agents Swager " src="https://github.com/user-attachments/assets/a811c1a9-6f0d-4619-a78b-a9e8db3971e5" />





