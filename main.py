import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Transaction, Budget, Category

app = FastAPI(title="Budget Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Budget Planner Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# -------------------- Schemas Endpoint for Viewer --------------------
class SchemaInfo(BaseModel):
    name: str
    fields: dict


@app.get("/schema")
def get_schema() -> dict:
    # Basic reflection of Pydantic models for the database viewer
    return {
        "category": Category.model_json_schema(),
        "budget": Budget.model_json_schema(),
        "transaction": Transaction.model_json_schema(),
    }


# -------------------- Budget Planner Endpoints --------------------
class CreateTransactionRequest(Transaction):
    pass


@app.post("/api/transactions")
def create_transaction(payload: CreateTransactionRequest):
    try:
        tx_id = create_document("transaction", payload)
        return {"id": tx_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/transactions")
def list_transactions(
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    tx_type: Optional[str] = Query(None, pattern="^(expense|income)$"),
):
    try:
        filter_dict = {}
        if category:
            filter_dict["category"] = category
        if tx_type:
            filter_dict["type"] = tx_type
        docs = get_documents("transaction", filter_dict, limit)
        # Convert ObjectId and datetime to serializable
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
            for k, v in list(d.items()):
                if isinstance(v, datetime):
                    d[k] = v.isoformat()
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateBudgetRequest(Budget):
    pass


@app.post("/api/budgets")
def create_budget(payload: CreateBudgetRequest):
    try:
        bid = create_document("budget", payload)
        return {"id": bid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/budgets")
def list_budgets(month: Optional[int] = None, year: Optional[int] = None, category: Optional[str] = None, limit: int = 100):
    try:
        filter_dict = {}
        if month is not None:
            filter_dict["month"] = month
        if year is not None:
            filter_dict["year"] = year
        if category is not None:
            filter_dict["category"] = category
        docs = get_documents("budget", filter_dict, limit)
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
            for k, v in list(d.items()):
                if isinstance(v, datetime):
                    d[k] = v.isoformat()
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CreateCategoryRequest(Category):
    pass


@app.post("/api/categories")
def create_category(payload: CreateCategoryRequest):
    try:
        cid = create_document("category", payload)
        return {"id": cid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories")
def list_categories(limit: int = 100):
    try:
        docs = get_documents("category", {}, limit)
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
            for k, v in list(d.items()):
                if isinstance(v, datetime):
                    d[k] = v.isoformat()
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
