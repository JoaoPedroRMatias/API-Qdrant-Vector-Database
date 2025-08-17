from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from auth import verify_token, create_access_token
from qdrant import Qdrant


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "user" and form_data.password == "123456":
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")


@app.get("/status")
def get_status(username: str = Depends(verify_token)):
    return {"status": "ok", "user": username}


@app.post("/collection/create")
def process_item(item: Item, username: str = Depends(verify_token)):
    return {
        "status": "received",
        "user": username,
        "name": item.name,
        "value": item.value,
        "double": item.value * 2
    }
