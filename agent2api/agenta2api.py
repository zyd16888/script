import json
import os
import time
import uuid
import threading
from typing import Any, AsyncGenerator, Dict, List, Optional, NamedTuple
from dataclasses import dataclass

import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

# Agenta Configuration
AGENTA_CHAT_URL = "https://cloud.agenta.ai/services/chat/test"
AGENTA_BILLING_URL = "https://cloud.agenta.ai/api/billing/usage"
AGENTA_REFRESH_URL = "https://cloud.agenta.ai/api/auth/session/refresh"
MIN_BALANCE_THRESHOLD = 100
MAX_CONSECUTIVE_FAILURES = 3
KEY_RECHECK_INTERVAL = 3600
BALANCE_REFRESH_INTERVAL = 600
TOKEN_REFRESH_INTERVAL = 60  # 1 minute

@dataclass
class AgentaKey:
    auth_token: str
    refresh_token: str
    project_id: str
    app_id: str
    balance: Optional[int] = None
    failures: int = 0
    last_checked: float = 0.0
    last_used: float = 0.0
    is_functional: bool = False

# Global variables
VALID_CLIENT_KEYS: set = set()
agenta_keys: List[AgentaKey] = []
current_key_index: int = 0
key_lock = threading.Lock()
models_data: Dict[str, List[Any]] = {"data": []}



# Pydantic Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str

class ModelList(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

class ChatCompletionChoice(BaseModel):
    message: ChatMessage
    index: int = 0
    finish_reason: str = "stop"

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionChoice]
    usage: Dict[str, int] = Field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})

class StreamChoice(BaseModel):
    delta: Dict[str, Any] = Field(default_factory=dict)
    index: int = 0
    finish_reason: Optional[str] = None

class StreamResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[StreamChoice]

# FastAPI App
app = FastAPI(title="Agenta OpenAI API Adapter")
security = HTTPBearer(auto_error=False)

def load_models() -> Dict[str, List[ModelInfo]]:
    """Load models from models.json"""
    global models_data
    try:
        with open("models.json", "r", encoding="utf-8") as f:
            raw_models = json.load(f)
        
        model_list = []
        for provider, models in raw_models.items():
            for model_id in models:
                model_list.append(ModelInfo(
                    id=model_id,
                    created=int(time.time()),
                    owned_by=provider
                ))
        
        models_data = {"data": model_list}
        print(f"Loaded {len(model_list)} models from models.json")
    except Exception as e:
        print(f"Error loading models.json: {e}")
        models_data = {"data": []}
    return models_data

def load_client_api_keys():
    """Load client API keys from client_api_keys.json"""
    global VALID_CLIENT_KEYS
    try:
        with open("client_api_keys.json", "r", encoding="utf-8") as f:
            keys = json.load(f)
            VALID_CLIENT_KEYS = set(keys) if isinstance(keys, list) else set()
            print(f"Loaded {len(VALID_CLIENT_KEYS)} client API keys.")
    except Exception as e:
        print(f"Error loading client_api_keys.json: {e}")
        VALID_CLIENT_KEYS = set()

def load_agenta_keys():
    """Load Agenta keys from agenta.txt"""
    global agenta_keys
    try:
        with open("agenta.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split("----")
                    if len(parts) >= 4:
                        agenta_keys.append(AgentaKey(
                            auth_token=parts[0],
                            refresh_token=parts[1],
                            project_id=parts[2],
                            app_id=parts[3]
                        ))
        print(f"Loaded {len(agenta_keys)} Agenta keys")
    except Exception as e:
        print(f"Error loading agenta.txt: {e}")

async def refresh_key_tokens(key: AgentaKey) -> bool:
    """Refresh auth and refresh tokens for a key"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Cookie": f'sRefreshToken="{key.refresh_token}"; sAccessToken="{key.auth_token}"'
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(AGENTA_REFRESH_URL, headers=headers)
            
            if response.status_code == 200:
                # Extract new tokens
                new_auth_token = response.headers.get("st-access-token")
                new_refresh_cookie = response.cookies.get("sRefreshToken")
                
                if new_auth_token and new_refresh_cookie:
                    # Parse refresh token from cookie
                    new_refresh_token = new_refresh_cookie.split('"')[1] if '"' in new_refresh_cookie else new_refresh_cookie
                    
                    # Update key
                    key.auth_token = new_auth_token
                    key.refresh_token = new_refresh_token
                    key.last_used = time.time()
                    key.failures = 0
                    
                    return True
                    
            return False
    except Exception:
        return False

def save_agenta_keys():
    """Save current agenta keys to file"""
    try:
        with open("agenta.txt", "w", encoding="utf-8") as f:
            f.write("# Agenta keys: auth_token----refresh_token----project_id----app_id\n")
            for key in agenta_keys:
                if key.is_functional:  # Only save functional keys
                    f.write(f"{key.auth_token}----{key.refresh_token}----{key.project_id}----{key.app_id}\n")
    except Exception as e:
        print(f"Error saving agenta.txt: {e}")

async def check_key_balance(key: AgentaKey, auto_refresh: bool = False) -> bool:
    """Check balance for a single key"""
    try:
        url = f"{AGENTA_BILLING_URL}?project_id={key.project_id}"
        headers = {"Cookie": f"sAccessToken={key.auth_token}"}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                key.balance = data.get("traces", {}).get("free", 0)
                key.last_checked = time.time()
                key.is_functional = key.balance >= MIN_BALANCE_THRESHOLD
                key.failures = 0
                
                # Only refresh token if explicitly requested (not during startup)
                if auto_refresh and key.is_functional:
                    await refresh_key_tokens(key)
                    save_agenta_keys()
                
                return True
            elif response.status_code in [401, 403]:
                # Try to refresh token first
                if await refresh_key_tokens(key):
                    return await check_key_balance(key, auto_refresh)  # Retry with new token
                else:
                    key.is_functional = False
                    key.balance = 0
                    return False
            else:
                key.failures += 1
                if key.failures >= MAX_CONSECUTIVE_FAILURES:
                    key.is_functional = False
                return False
    except Exception:
        key.failures += 1
        if key.failures >= MAX_CONSECUTIVE_FAILURES:
            key.is_functional = False
        return False

async def initial_check_keys():
    """Check all keys on startup - concurrent execution"""
    if agenta_keys:
        print(f"Checking {len(agenta_keys)} Agenta keys concurrently...")
        # Use asyncio.gather for concurrent execution
        import asyncio
        await asyncio.gather(*[check_key_balance(key) for key in agenta_keys], return_exceptions=True)
        functional_count = sum(1 for key in agenta_keys if key.is_functional)
        print(f"Found {functional_count} functional keys out of {len(agenta_keys)}")

def get_next_functional_key() -> Optional[AgentaKey]:
    """Get next functional key using round-robin"""
    global current_key_index
    
    with key_lock:
        functional_keys = [k for k in agenta_keys if k.is_functional]
        if not functional_keys:
            return None
        
        key = functional_keys[current_key_index % len(functional_keys)]
        current_key_index = (current_key_index + 1) % len(functional_keys)
        
        return key

def update_key_on_failure(key: AgentaKey, is_auth_error: bool = False):
    """Update key status on failure"""
    if is_auth_error:
        key.is_functional = False
        key.balance = 0
    else:
        key.failures += 1
        if key.failures >= MAX_CONSECUTIVE_FAILURES:
            key.is_functional = False

def background_refresh_thread():
    """Background thread to refresh unused keys every 10 minutes"""
    import asyncio
    
    async def refresh_unused_keys():
        while True:
            try:
                await asyncio.sleep(TOKEN_REFRESH_INTERVAL)
                current_time = time.time()
                
                for key in agenta_keys[:]:  # Copy list to allow modification
                    if key.is_functional and (current_time - key.last_used) > TOKEN_REFRESH_INTERVAL:
                        success = await refresh_key_tokens(key)
                        if not success:
                            # Remove permanently failed keys
                            key.is_functional = False
                            agenta_keys.remove(key)
                            print(f"Removed permanently failed key for project {key.project_id}")
                
                # Save updated keys
                save_agenta_keys()
                
            except Exception as e:
                print(f"Background refresh error: {e}")
    
    # Run in asyncio event loop
    try:
        asyncio.run(refresh_unused_keys())
    except Exception as e:
        print(f"Background thread error: {e}")

def get_model_item(model_id: str) -> Optional[ModelInfo]:
    """Get model item by ID"""
    for model in models_data.get("data", []):
        if model.id == model_id:
            return model
    return None

async def authenticate_client(auth: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Authenticate client"""
    if not VALID_CLIENT_KEYS:
        raise HTTPException(status_code=503, detail="Service unavailable: No client API keys configured.")
    
    if not auth or auth.credentials not in VALID_CLIENT_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key.")

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    print("Starting Agenta OpenAI API Adapter...")
    load_models()
    load_client_api_keys()
    load_agenta_keys()
    await initial_check_keys()
    
    # Start background refresh thread
    import threading
    refresh_thread = threading.Thread(target=background_refresh_thread, daemon=True)
    refresh_thread.start()
    
    print("Server initialization completed.")

@app.get("/v1/models", response_model=ModelList)
async def list_v1_models(_: None = Depends(authenticate_client)):
    """List available models - authenticated"""
    return ModelList(data=models_data.get("data", []))

@app.get("/models", response_model=ModelList)
async def list_models_no_auth():
    """List available models without authentication"""
    return ModelList(data=models_data.get("data", []))

@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    _: None = Depends(authenticate_client)
):
    """Create chat completion using Agenta backend"""
    # Get functional key
    key = get_next_functional_key()
    if not key:
        raise HTTPException(status_code=503, detail="No functional Agenta keys available.")
    
    # Validate model
    if not get_model_item(request.model):
        raise HTTPException(status_code=404, detail=f"Model '{request.model}' not found.")
    
    # Extract system message
    system_content = "You are a helpful assistant."
    user_messages = []
    for msg in request.messages:
        if msg.role == "system":
            system_content = msg.content
        else:
            user_messages.append({"role": msg.role, "content": msg.content})
    
    # Build Agenta payload
    payload = {
        "ag_config": {
            "prompt": {
                "messages": [{"role": "system", "content": f"\n{system_content}"}],
                "template_format": "curly",
                "input_keys": ["context"],
                "llm_config": {
                    "model": request.model,
                    "max_tokens": request.max_tokens or 16384,
                    "top_p": request.top_p or 1.0,
                    "temperature": request.temperature or 0.1,
                    "tools": []
                }
            }
        },
        "inputs": {"context": system_content},
        "messages": user_messages
    }
    
    headers = {
        "Authorization": f"Bearer {key.auth_token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    url = f"{AGENTA_CHAT_URL}?project_id={key.project_id}&application_id={key.app_id}"
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Refresh token immediately after successful API call
            refresh_success = await refresh_key_tokens(key)
            if refresh_success:
                save_agenta_keys()
            else:
                print(f"Warning: Failed to refresh token for key {key.project_id}")
            
            # Parse response - extract final assistant content
            final_content = ""
            for line in response.text.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        if (data.get("data", {}).get("role") == "assistant" and 
                            "content" in data.get("data", {})):
                            final_content = data["data"]["content"]
                    except json.JSONDecodeError:
                        continue
            
            # Return response
            if request.stream:
                async def stream_generator():
                    stream_id = f"chatcmpl-{uuid.uuid4().hex}"
                    created = int(time.time())
                    
                    # Role delta
                    yield f"data: {StreamResponse(id=stream_id, created=created, model=request.model, choices=[StreamChoice(delta={'role': 'assistant'})]).json()}\n\n"
                    
                    # Content delta
                    if final_content:
                        yield f"data: {StreamResponse(id=stream_id, created=created, model=request.model, choices=[StreamChoice(delta={'content': final_content})]).json()}\n\n"
                    
                    # Finish
                    yield f"data: {StreamResponse(id=stream_id, created=created, model=request.model, choices=[StreamChoice(delta={}, finish_reason='stop')]).json()}\n\n"
                    yield "data: [DONE]\n\n"
                
                return StreamingResponse(stream_generator(), media_type="text/event-stream")
            else:
                return ChatCompletionResponse(
                    model=request.model,
                    choices=[ChatCompletionChoice(message=ChatMessage(role="assistant", content=final_content))]
                )
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code in [401, 403]:
            # Try refreshing token and retrying once
            if await refresh_key_tokens(key):
                save_agenta_keys()
                # Retry the request with new token
                headers["Authorization"] = f"Bearer {key.auth_token}"
                try:
                    async with httpx.AsyncClient(timeout=120.0) as client:
                        response = await client.post(url, json=payload, headers=headers)
                        response.raise_for_status()
                        
                        # Parse and return response (same logic as above)
                        final_content = ""
                        for line in response.text.strip().split('\n'):
                            if line.strip():
                                try:
                                    data = json.loads(line)
                                    if (data.get("data", {}).get("role") == "assistant" and 
                                        "content" in data.get("data", {})):
                                        final_content = data["data"]["content"]
                                except json.JSONDecodeError:
                                    continue
                        
                        if request.stream:
                            async def retry_stream_generator():
                                stream_id = f"chatcmpl-{uuid.uuid4().hex}"
                                created = int(time.time())
                                yield f"data: {StreamResponse(id=stream_id, created=created, model=request.model, choices=[StreamChoice(delta={'role': 'assistant'})]).json()}\n\n"
                                if final_content:
                                    yield f"data: {StreamResponse(id=stream_id, created=created, model=request.model, choices=[StreamChoice(delta={'content': final_content})]).json()}\n\n"
                                yield f"data: {StreamResponse(id=stream_id, created=created, model=request.model, choices=[StreamChoice(delta={}, finish_reason='stop')]).json()}\n\n"
                                yield "data: [DONE]\n\n"
                            return StreamingResponse(retry_stream_generator(), media_type="text/event-stream")
                        else:
                            return ChatCompletionResponse(
                                model=request.model,
                                choices=[ChatCompletionChoice(message=ChatMessage(role="assistant", content=final_content))]
                            )
                except Exception:
                    update_key_on_failure(key, is_auth_error=True)
                    raise HTTPException(status_code=503, detail="Agenta API error after retry")
            else:
                update_key_on_failure(key, is_auth_error=True)
        else:
            update_key_on_failure(key)
        raise HTTPException(status_code=e.response.status_code, detail=f"Agenta API error: {e.response.text}")
    except Exception as e:
        update_key_on_failure(key)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Create required files if missing
    if not os.path.exists("models.json"):
        print("ERROR: models.json not found.")
    
    if not os.path.exists("agenta.txt"):
        print("Creating dummy agenta.txt...")
        with open("agenta.txt", "w", encoding="utf-8") as f:
            f.write("# Add your Agenta keys here: auth_token----refresh_token----project_id----app_id\n")
            f.write("dummy_token----dummy_refresh_token----dummy_project----dummy_app\n")
    
    if not os.path.exists("client_api_keys.json"):
        dummy_key = f"sk-agenta-{uuid.uuid4().hex}"
        with open("client_api_keys.json", "w", encoding="utf-8") as f:
            json.dump([dummy_key], f, indent=2)
        print(f"Created client_api_keys.json with key: {dummy_key}")
    
    print("\n--- Agenta OpenAI API Adapter ---")
    print("Endpoints:")
    print("  GET  /v1/models")
    print("  GET  /models")
    print("  POST /v1/chat/completions")
    print("------------------------------------")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)