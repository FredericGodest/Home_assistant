import os
import sys
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import db_logger
from langchain_core.utils.uuid import uuid7
from agents import basic_agent, netrunner_agent
from router import route, AgentType

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LLM_API_KEY = os.getenv("API_KEY_MAMMOUTH")
GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY")

if not LLM_API_KEY:
    logger.critical("LLM_API_KEY non définie")
    sys.exit(1)

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)

def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if api_key != GATEWAY_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Clé API invalide")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db_logger.init_db()
    yield

app = FastAPI(title="Mistral Agent Gateway", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", dependencies=[Depends(verify_api_key)])
def ask(payload: dict):
    question = payload.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Champ 'question' manquant")
    
    # Routing
    agent_type = route(question)
    agent = netrunner_agent if agent_type == AgentType.NETRUNNER else basic_agent

    try:
        response = agent.invoke(
            {"messages": [("human", question)]},
            config={"configurable": {"thread_id": str(uuid7())}}
        )
        answer = response["messages"][-1].content.strip()
        db_logger.log(question, answer, status="success")


    except Exception as e:
        logger.exception("Erreur agent")
        db_logger.log(question, None, status="error")
        raise HTTPException(status_code=502, detail=str(e))

    return {"answer": answer}
