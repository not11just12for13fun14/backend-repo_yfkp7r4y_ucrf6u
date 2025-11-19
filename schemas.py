"""
Database Schemas for Budget Planner

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercase of the class name (e.g., Transaction -> "transaction").
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date as dt_date


class Category(BaseModel):
    """
    Categories collection schema
    Collection: "category"
    """
    name: str = Field(..., description="Category name (e.g., Groceries, Rent)")
    color: Optional[str] = Field(None, description="Hex color for UI tags")


class Budget(BaseModel):
    """
    Budgets collection schema
    Represents a monthly budget for a specific category (or overall if category is None)
    Collection: "budget"
    """
    month: int = Field(..., ge=1, le=12, description="Month number (1-12)")
    year: int = Field(..., ge=2000, le=3000, description="Four-digit year")
    amount: float = Field(..., ge=0, description="Budgeted amount for the period")
    category: Optional[str] = Field(None, description="Category this budget applies to. None = overall budget")


class Transaction(BaseModel):
    """
    Transactions collection schema
    Collection: "transaction"
    """
    type: Literal["expense", "income"] = Field("expense", description="Transaction type")
    amount: float = Field(..., gt=0, description="Positive amount")
    category: Optional[str] = Field(None, description="Category name for expenses/income")
    note: Optional[str] = Field(None, description="Short description or memo")
    date: dt_date = Field(..., description="Transaction date")
