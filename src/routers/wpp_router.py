import logging
from fastapi import APIRouter, HTTPException

from configs.config import logger
from container import transaction_service, redis_client
from validation import RequestModel

router = APIRouter(
    prefix="/wpp"
)


@router.post("/")
async def process_transaction(request: RequestModel):
    logger.info('Transaction came on the endpoint.')
    try:
        # Caching
        request_json = request.model_dump_json()
        logger.debug('Dumped request to json.')

        redis_client.rpush('REQUESTS', request_json)
        logger.debug('Pushed request to redis queue.')

        logger.debug('Starting working with database.')
        # Storing in DB
        await transaction_service.insert_transaction(request)
        logger.debug('Finished working with database.')

        response_data = {
            "description": "Transaction has been processed successfully",
            "statusCode": 200,
            "txnReference": request.transaction.txnReference
        }

        logger.info('Transaction processing is successful. Returning response...')
        return response_data
    except Exception as ex:
        logging.error(ex)
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "post_id": None,
            "details": "Server Error"
        })
