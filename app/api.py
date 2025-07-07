from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .rag_pipeline import generate_answer
import traceback

app = FastAPI()

class Question(BaseModel):
    query:str
    
@app.post('/ask')
def ask_question(item: Question):
    try:
        result = generate_answer(item.query)
        return result
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        raise HTTPException(status_code=500, detail=str(e))