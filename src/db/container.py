import redis

from db.transaction_service import TransactionService

transaction_service = TransactionService()
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
