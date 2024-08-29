import hashlib
import json
import logging
import time
import uuid
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from db.container import transaction_service
from validation import RequestModel

router = APIRouter(
    prefix="/wpp"
)


@router.post("/")
async def process_transaction(request: RequestModel):
    request_json = json.dumps(request.dict(), sort_keys=True)
    cache_key = hashlib.sha256(request_json.encode('utf-8')).hexdigest()

    cached_request = await FastAPICache.get_backend().get(cache_key)
    if cached_request:
        return json.loads(cached_request)

    await transaction_service.insert_transaction(request)

    response_data = {
        "description": "Transaction has been processed successfully",
        "statusCode": 200,
        "txnReference": request.transaction.txnReference
    }

    await FastAPICache.get_backend().set(cache_key, request_json, expire=60 * 10)

    return response_data
