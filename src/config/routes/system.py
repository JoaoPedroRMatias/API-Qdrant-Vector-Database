from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from core.auth import verify_token, create_access_token
from qdrant import QdrantCollection, Qdrant
from core.models import NameCollection, DocumentCreate, DocumentSearch
import traceback

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# TEST AND AUTH ROUTES
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "user" and form_data.password == "123456":
        access_token = create_access_token(
            data={"sub": form_data.username},
            expires_delta=timedelta(minutes=30)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Credenciais inválidas")


@router.get("/status", dependencies=[Depends(verify_token)])
def get_status():
    try:
        return {"status": True, "message": "Rota funcionando."}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Nome inválido: {e}")

    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}\nTraceback:\n{tb}"
        )


# COLLECTIONS ROUTES
@router.post("/collection/create", dependencies=[Depends(verify_token)])
def create_collection(name_collection: NameCollection):
    try:
        q_collection = QdrantCollection()
        q_collection.create_collection(name_collection.name_collection)

        return {
            "error": False,
            "message": "Collection created successfully!."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Nome inválido: {e}")

    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}\nTraceback:\n{tb}"
        )


@router.post("/collection/info", dependencies=[Depends(verify_token)])
def get_collection_info(name_collection: NameCollection):
    try:
        q_collection = QdrantCollection()
        return {
            "result": q_collection.collection_info(name_collection.name_collection)
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Nome inválido: {e}")

    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}\nTraceback:\n{tb}"
        )


# EMBEDDINGS ROUTES
@router.post("/embedding/create", dependencies=[Depends(verify_token)])
def create_embedding(document_create: DocumentCreate):
    try:
        title = document_create.title
        description = document_create.description

        q_embedding = Qdrant()
        data = q_embedding.add_document(title, description)

        return {"error": False, "message": "Embedding created successfully!"}

    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}\nTraceback:\n{tb}"
        )


@router.post("/embedding/search", dependencies=[Depends(verify_token)])
def search_embedding(document_search: DocumentSearch):
    try:
        query = document_search.query
        limit = 1 if document_search.limit == 0 else document_search.limit

        q_embedding = Qdrant()
        data = q_embedding.search(query, limit)

        return data

    except Exception as e:
        tb = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}\nTraceback:\n{tb}"
        )
