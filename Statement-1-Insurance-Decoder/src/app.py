from fastapi import FastAPI
from pydantic import BaseModel
from rag import ask
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str
    filter: str = "all"

@app.post("/api")
def handle_query(q: Query):
    return ask(q.question, q.filter)