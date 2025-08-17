from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from auth import verify_token, create_access_token
from qdrant import Qdrant, QdrantCollection
from models import NameCollection


app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# TEST AND AUTH ROUTES
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "user" and form_data.password == "123456":
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Credenciais inválidas")


@app.get("/status", dependencies=[Depends(verify_token)])
def get_status():
    try:
        return {"status": True, "message": "Rota funcionando."}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Nome inválido: {e}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


# COLLECTIONS ROUTES
@app.post("/collection/create", dependencies=[Depends(verify_token)])
def process_item(name_collection: NameCollection):
    try:
        q_collection = QdrantCollection()
        q_collection.create_collection(name_collection.name_collection)

        return {
            "status": True,
            "message": "Collection criada com sucesso."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Nome inválido: {e}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.post("/collection/info", dependencies=[Depends(verify_token)])
def process_item(name_collection: NameCollection):
    try:
        q_collection = QdrantCollection()

        return {
            "status": True,
            "result": q_collection.collection_info(name_collection.name_collection)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Nome inválido: {e}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")