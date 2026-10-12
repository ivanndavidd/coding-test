# small HTTP API on top of vector_db.py so it can be deployed
# run: uvicorn api:app --port 8001

from fastapi import FastAPI
from pydantic import BaseModel
from vector_db import VectorDB

app = FastAPI()
db = VectorDB("data/vectors.json")


class AddRequest(BaseModel):
    id: str
    vector: list[float]
    text: str = ""


class SearchRequest(BaseModel):
    vector: list[float]
    top_k: int = 3


@app.post("/add")
def add(req: AddRequest):
    db.add(req.id, req.vector, req.text)
    return {"ok": True, "total": len(db.data)}


@app.post("/search")
def search(req: SearchRequest):
    results = db.search(req.vector, req.top_k)
    return [{"score": s, "id": item["id"], "text": item["text"]} for s, item in results]
