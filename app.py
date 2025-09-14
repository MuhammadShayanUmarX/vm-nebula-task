import os
import time
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import google.generativeai as genai
import httpx
from dotenv import load_dotenv
from database import db_manager


load_dotenv()



GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
Z_API_KEY = os.getenv("Z_API_KEY")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini Flash initialized")
else:
    print("Gemini API key not found")

# FastAPI 
app = FastAPI(
    title="VM Nebula Task",
    description="Multi-LLM FastAPI backend with intelligent agent routing",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    agent_used: str
    response: str
    model: str
    confidence: float
    processing_time: float
    token_count: int

# Agent Detection - Part 2: Agent Specialization
def detect_agent(query: str) -> str:
    """Detect which agent should handle the query based on keywords"""
    query_lower = query.lower()
    
    # Code Assistant 
    code_keywords = ["code", "function", "debug", "programming", "python", "javascript", 
                    "error", "bug", "syntax", "algorithm", "script", "class", "method"]
    
    # Research Assistant 
    research_keywords = ["research", "analyze", "compare", "find", "study", "investigate",
                        "information", "data", "facts", "explain", "analysis", "summary"]
    
    # Task Helper 
    task_keywords = ["how to", "steps", "guide", "tutorial", "help", "process", 
                    "instruction", "walkthrough", "procedure", "setup"]
    
    # Check for matches
    if any(keyword in query_lower for keyword in code_keywords):
        return "code"
    elif any(keyword in query_lower for keyword in research_keywords):
        return "research"
    elif any(keyword in query_lower for keyword in task_keywords):
        return "task"
    else:
        return "task"  

# Model Selection - Part 1: Intelligent Routing
def choose_model(query: str, agent: str) -> str:
    """Choose best model based on query complexity and cost optimization"""
    word_count = len(query.split())
    
    # Cost optimization logic 
    if word_count < 15:  
        return "gemini-flash-8b"
    elif agent == "code":  
        return "gemini-flash"
    elif word_count > 50:  
        return "zai-large"
    else:
        return "gemini-flash"  

# LLM Integration Functions
async def call_gemini_flash(query: str, model: str) -> Dict:
    """Call Google Gemini Flash models"""
    try:
        start_time = time.time()
        
        # Choose the right Gemini model
        if model == "gemini-flash-8b":
            model_name = "gemini-1.5-flash-8b"
        else:
            model_name = "gemini-1.5-flash"
        
        llm = genai.GenerativeModel(model_name)
        response = llm.generate_content(query)
        
        processing_time = time.time() - start_time
        token_count = len(response.text.split())
        
        return {
            "response": response.text,
            "confidence": 0.9,
            "processing_time": processing_time,
            "token_count": token_count,
            "success": True
        }
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return {
            "response": f"Gemini error: {str(e)}",
            "confidence": 0.0,
            "processing_time": 0.0,
            "token_count": 0,
            "success": False
        }

async def call_zai_direct(query: str) -> Dict:
    """Call Z.ai directly (not via OpenRouter)"""
    try:
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {Z_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "zai-large",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.z.ai/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
        
        processing_time = time.time() - start_time
        content = result["choices"][0]["message"]["content"]
        token_count = result.get("usage", {}).get("total_tokens", len(content.split()))
        
        return {
            "response": content,
            "confidence": 0.85,
            "processing_time": processing_time,
            "token_count": token_count,
            "success": True
        }
        
    except Exception as e:
        print(f"Z.ai error: {e}")
        return {
            "response": f"Z.ai error: {str(e)}",
            "confidence": 0.0,
            "processing_time": 0.0,
            "token_count": 0,
            "success": False
        }

# Main LLM Router with Fallback Mechanism
async def call_llm(model: str, query: str, agent: str) -> Dict:
    """Route to appropriate LLM with fallback mechanism"""
    agent_prompts = {
        "code": "You are a Code Assistant. Provide detailed code analysis and explanations:\n\n",
        "research": "You are a Research Assistant. Provide comprehensive analysis and information:\n\n", 
        "task": "You are a Task Helper. Provide step-by-step guidance:\n\n"
    }
    
    full_query = agent_prompts.get(agent, "") + query
    
    # Try primary model
    if model.startswith("gemini"):
        result = await call_gemini_flash(full_query, model)
    elif model == "zai-large":
        result = await call_zai_direct(full_query)
    else:
        result = await call_gemini_flash(full_query, "gemini-flash")
    
    # Fallback mechanism 
    if not result.get("success", False):
        print(f"Primary model {model} failed, trying fallback...")
        if model != "gemini-flash":
            result = await call_gemini_flash(full_query, "gemini-flash")
        if not result.get("success", False) and Z_API_KEY:
            result = await call_zai_direct(full_query)
    
    return result

# API Endpoints

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat interface - Routes user queries to specialized AI agents"""
    # Generate session ID (if not provided)
    session_id = request.session_id or f"sess_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    # Agent Detection
    agent = detect_agent(request.query)
    
    # Model Selection with Cost Optimization
    model = choose_model(request.query, agent)
    
    # Call LLM with Fallback
    result = await call_llm(model, request.query, agent)
    
    # Save to database
    db_manager.save_session(session_id, request.query, result, agent, model)
    
    return ChatResponse(
        agent_used=agent,
        response=result["response"],
        model=model,
        confidence=result["confidence"],
        processing_time=result["processing_time"],
        token_count=result["token_count"]
    )

@app.get("/models/status")
async def get_models_status():
    """Get health status of available models"""
    models = []
    
    # Check Gemini models
    if GEMINI_API_KEY:
        models.extend([
            {"model": "gemini-flash", "status": "available", "provider": "google"},
            {"model": "gemini-flash-8b", "status": "available", "provider": "google"}
        ])
    
    # Check Z.ai model
    if Z_API_KEY:
        models.append({"model": "zai-large", "status": "available", "provider": "zai"})
    
    return {
        "models": models,
        "total_models": len(models),
        "healthy_models": len([m for m in models if m["status"] == "available"]),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """Streaming responses using Server-Sent Events"""
    session_id = request.session_id or f"sess_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    async def generate_stream():
        try:
            # Send start event
            yield f"data: {json.dumps({'event': 'start', 'agent': detect_agent(request.query)})}\n\n"
            
            # Get response
            agent = detect_agent(request.query)
            model = choose_model(request.query, agent)
            result = await call_llm(model, request.query, agent)
            
            # Stream response in chunks
            response_text = result["response"]
            words = response_text.split()
            
            for i in range(0, len(words), 5): 
                chunk = " ".join(words[i:i+5])
                yield f"data: {json.dumps({'event': 'delta', 'content': chunk})}\n\n"
                await asyncio.sleep(0.1)  
            
            # Send completion 
            yield f"data: {json.dumps({'event': 'complete', 'model': model, 'confidence': result['confidence']})}\n\n"
            
            # Save session
            db_manager.save_session(session_id, request.query, result, agent, model)
            
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"
    
    return EventSourceResponse(generate_stream())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    available_keys = sum(1 for key in [GEMINI_API_KEY, Z_API_KEY] if key)
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_available": available_keys
    }

@app.get("/sessions/recent")
async def get_recent_sessions(limit: int = 20):
    """Get recent chat sessions"""
    return db_manager.get_recent_sessions(limit)

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 10):
    """Get chat history for a specific session"""
    return db_manager.get_session_history(session_id, limit)

@app.get("/stats/models")
async def get_model_stats():
    """Get usage statistics for different models"""
    return db_manager.get_model_stats()

@app.get("/stats/agents")
async def get_agent_stats():
    """Get usage statistics for different agents"""
    return db_manager.get_agent_stats()

@app.delete("/sessions/cleanup")
async def cleanup_old_sessions(days: int = 30):
    """Clean up sessions older than specified days"""
    deleted_count = db_manager.cleanup_old_sessions(days)
    return {"deleted_sessions": deleted_count, "days": days}

# Run the application
if __name__ == "__main__":
    import uvicorn
    print("Starting Smart AI Assistant...")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)