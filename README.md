# API Qdrant Vector Database

**API REST em FastAPI para criar, indexar e buscar documentos por similaridade semântica usando Qdrant.**

Recebe texto (título + descrição), gera embeddings multilíngues localmente com `fastembed` e armazena/consulta vetores no Qdrant. Autenticação via JWT (OAuth2 Bearer).

## Funcionalidades

- Criação de coleções no Qdrant com configuração otimizada (quantização int8, HNSW, on-disk)
- Indexação de documentos com embeddings gerados localmente (sem depender de API externa)
- Busca semântica por similaridade de cosseno, com filtro por score e limite de resultados
- Autenticação JWT (login → Bearer token)
- Cache de embeddings em memória para textos repetidos

## Quick Start

```bash
cp .env.example .env   # preencha SECRET_KEY, QDRANT_API_KEY etc.
docker compose up --build
```

API disponível em `http://localhost:9090` (Swagger em `/docs`, exceto em produção).
Qdrant disponível em `http://localhost:6333`.

## Requisitos

- Docker e Docker Compose
- ou, rodando local: Python 3.11+, ~1 GB livre para cache do modelo de embedding (baixado no primeiro uso)

## Configuração (`.env`)

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Chave usada para assinar os tokens JWT |
| `ALGORITHM` | Algoritmo JWT (ex: `HS256`) |
| `QDRANT_URL` | `http://qdrant:6333` via docker-compose, `http://localhost:6333` se a API rodar fora do Docker |
| `QDRANT_API_KEY` | API key usada pelo client da aplicação para autenticar no Qdrant |
| `QDRANT__SERVICE__API_KEY` | Mesma API key, lida pelo próprio serviço Qdrant para exigir autenticação |
| `ENV` | `development` habilita `/docs`; qualquer outro valor desabilita |

## Uso

### 1. Login

```bash
curl -X POST http://localhost:9090/login \
  -d "username=user&password=123456"
```

Retorna `access_token`. Use em todas as rotas seguintes como `Authorization: Bearer <token>`.

### 2. Criar coleção

```bash
curl -X POST http://localhost:9090/collection/create \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"name_collection": "documents"}'
```

> A coleção precisa existir antes de indexar documentos — não é criada automaticamente.

### 3. Indexar documento

```bash
curl -X POST http://localhost:9090/embedding/create \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"title": "Guia de gatos", "description": "Como cuidar de filhotes"}'
```

### 4. Buscar por similaridade

```bash
curl -X POST http://localhost:9090/embedding/search \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"query": "cuidados com filhote de gato", "limit": 5}'
```

## Rotas

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| POST | `/login` | não | Gera token JWT |
| GET | `/status` | sim | Healthcheck |
| POST | `/collection/create` | sim | Cria coleção no Qdrant |
| POST | `/collection/info` | sim | Retorna informações de uma coleção |
| POST | `/embedding/create` | sim | Gera embedding e indexa documento |
| POST | `/embedding/search` | sim | Busca documentos por similaridade |

## Tech Stack

| Camada | Stack |
|---|---|
| API | FastAPI + Uvicorn |
| Auth | JWT via `python-jose`, OAuth2 Password Flow |
| Embeddings | `fastembed` (`paraphrase-multilingual-mpnet-base-v2`, 768 dim) |
| Banco vetorial | Qdrant (gRPC) |
| Infra | Docker Compose (API + Qdrant) |

## Estrutura do projeto

```
.
├── app.py                       # entrypoint FastAPI
├── docker-compose.yml           # serviços api + qdrant
├── Dockerfile
└── src/
    ├── config/
    │   ├── settings.py           # variáveis de ambiente
    │   └── routes/system.py      # rotas HTTP
    ├── core/
    │   ├── auth/                 # geração/verificação de JWT
    │   └── models/                # schemas Pydantic
    └── qdrant/
        ├── collection.py         # criação/consulta de coleções
        └── embeddings.py         # geração de embeddings + upsert/search
```

## Desenvolvimento local (sem Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export QDRANT_URL=http://localhost:6333
uvicorn app:app --reload --port 9090 --app-dir src
```

Requer um Qdrant rodando separadamente (`docker run -p 6333:6333 qdrant/qdrant`).
