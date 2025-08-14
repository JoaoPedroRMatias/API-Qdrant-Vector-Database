from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from models import QuestionRequest
from auth import verify_token, create_access_token


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "doctor" and form_data.password == "147/258*":
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

