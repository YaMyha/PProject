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
    """
    Processes a transaction by adding it to a Redis queue and storing it in the database.

    Args:
        request (RequestModel): The transaction request data containing transaction, merchant, and customer details.

    Returns:
        dict: A response dictionary containing the status and transaction reference.

    Raises:
        HTTPException: If there is an error during processing, a 500 status code is returned with details.

    Example:
        Request:
        {
          "lang": "string",
          "merchant": {
            "merchantID": "string00",
            "customerID": "string00"
          },
          "customer": {
            "billingAddress": {
              "firstName": "string",
              "lastName": "string",
              "mobileNo": "string",
              "emailId": "user@example.com",
              "addressLine1": "string",
              "city": "string",
              "state": "string",
              "zip": "string",
              "country": "st"
            }
          },
          "transaction": {
            "txnAmount": 0,
            "paymentType": "string",
            "currencyCode": "string",
            "txnReference": "string",
            "seriestype": "string",
            "method": "string",
            "paymentDetail": {
              "cardNumber": "string",
              "cardType": "string",
              "expYear": 0,
              "expMonth": 0,
              "nameOnCard": "string",
              "saveDetails": true,
              "cvv": "string"
            },
            "url": {
              "successURL": "string",
              "failURL": "string"
            }
          }
        }

        Response:
        {
            "description": "Transaction has been processed successfully",
            "statusCode": 200,
            "txnReference": "txn123"
        }
    """

    logger.info('Transaction came on the endpoint.')
    try:
        # Caching
        request_json = request.model_dump_json()
        logger.debug('Dumped request to json.')

        redis_client.rpush('REQUESTS', request_json)
        logger.debug('Pushed request to redis queue.')

        # Storing in DB
        logger.debug('Starting working with database.')
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
