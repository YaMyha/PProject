import logging
from fastapi import APIRouter, HTTPException

from db.container import transaction_service, redis_client
from validation import RequestModel

router = APIRouter(
    prefix="/wpp"
)


@router.post("/")
async def process_transaction(request: RequestModel):
    try:
        # Caching
        request_json = request.model_dump_json()
        redis_client.rpush('REQUESTS', request_json)

        # Storing in DB
        await transaction_service.insert_transaction(request)

        response_data = {
            "description": "Transaction has been processed successfully",
            "statusCode": 200,
            "txnReference": request.transaction.txnReference
        }

        return response_data
    except Exception as ex:
        logging.error(ex)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "post_id": None,
            "details": "Server Error"
        })
