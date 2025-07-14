from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from chroma_client import ChromaClient
from models import QuestionRequest
from deepseek import request_deep
from auth import verify_token, create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "doctor" and form_data.password == "147/258*":
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")


@app.post("/question")
def read_root(request_data: QuestionRequest, token: str = Depends(verify_token)):
    question = request_data.question

    chroma = ChromaClient()
    similar_search = chroma.get_db(question)

    response = request_deep(f"""
    Com base no conteúdo do banco vetorial: 
    {similar_search["documents"][0]}\n
                                        
    {question}
    """)

    output_json = {
        "metadata": similar_search["metadatas"],
        "result": response.json()["choices"][0]["message"]["content"]
    }

    return output_json
