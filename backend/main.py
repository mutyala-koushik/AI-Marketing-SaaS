from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import os

# Database
from database.database import Base, engine

# Routes
from routes.customers import router as customer_router
from routes.strategy import router as strategy_router
from routes.campaign import router as campaign_router
from routes.evaluation import router as evaluation_router
from routes.history import router as history_router
from routes.performance import router as performance_router
from routes.content import router as content_router

# Services (RAG Engine)
from services.rag_service import rag_engine, retrieve_policy_context

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Load ML Artifacts (XGBoost + TreeSHAP)
    app.state.ml = {}
    try:
        if os.path.exists("artifacts/xgb_churn_model.joblib"):
            app.state.ml["model"] = joblib.load("artifacts/xgb_churn_model.joblib")
        if os.path.exists("artifacts/shap_explainer.joblib"):
            app.state.ml["explainer"] = joblib.load("artifacts/shap_explainer.joblib")
        if os.path.exists("artifacts/encoders.joblib"):
            app.state.ml["encoders"] = joblib.load("artifacts/encoders.joblib")
        print("ML artifacts loaded successfully.")
    except Exception as e:
        print(f"Warning: Could not load some ML artifacts: {e}")

    # 2. Attach RAG Singleton Engine to App State
    app.state.rag = rag_engine
    print(f"RAG Engine initialized with {len(rag_engine.documents)} policy documents.")

    yield

    # Clean up state on shutdown
    app.state.ml.clear()

app = FastAPI(
    title="AI Marketing SaaS",
    description="Adaptive AI-powered marketing intelligence platform with Explainable AI & RAG",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route registrations
app.include_router(customer_router)
app.include_router(strategy_router)
app.include_router(campaign_router)
app.include_router(evaluation_router)
app.include_router(history_router)
app.include_router(performance_router)
app.include_router(content_router)

@app.get("/")
def root():
    return {
        "message": "AI Marketing SaaS API is running",
        "status": "success",
        "engines": {
            "ml_diagnostics": "XGBoost + TreeSHAP",
            "qualitative_grounding": "Lightweight Vector RAG",
            "generative_synthesis": "Gemini 3.5 Flash",
        },
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "ml_loaded": bool(app.state.ml.get("model")),
        "rag_ready": bool(hasattr(app.state, "rag")),
    }

# Dedicated inspection route to demonstrate live RAG retrieval in viva
@app.get("/rag/inspect")
def inspect_rag(query: str = "Contract"):
    policy = retrieve_policy_context(query)
    return {
        "query": query,
        "retrieved_policy": policy,
        "similarity_metric": "Cosine Similarity",
        "total_documents_indexed": len(rag_engine.documents),
    }