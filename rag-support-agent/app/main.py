from fastapi import FastAPI, HTTPException, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.pydantic_models import ChatRequest
from app.langchain_utils import get_qa_chain
from fastapi.middleware.cors import CORSMiddleware

# Initialize the limiter tracking by IP address
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="RAG Support Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://rag-frontend-omega-one.vercel.app"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach the limiter to the app and register the custom error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

qa_chain = get_qa_chain()

@app.get("/")
def read_root():
    return {"status": "Agent is running inside Docker"}

@app.post("/api/chat")
@limiter.limit("5/minute") # Allow 5 questions per minute per IP
def chat_with_agent(request: Request, chat_request: ChatRequest):
    if qa_chain is None:
        raise HTTPException(status_code=500, detail="QA Chain failed to load.")
    
    try:
        response = qa_chain.invoke(
            {"question": chat_request.question,
             "department": chat_request.department},
            
            config={"configurable": {"session_id": chat_request.session_id}}
        )
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))