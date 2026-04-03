from fastapi import APIRouter

from app.api.v1 import ai, auth, finance, transactions


api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(transactions.router)
api_router.include_router(finance.router)
api_router.include_router(ai.router)

