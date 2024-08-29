import uvicorn
from fastapi import FastAPI

from configs.config import logger
from routers.wpp_router import router


app = FastAPI(title="Test Task", debug=True)
logger.info("Application created.")

app.include_router(router)
logger.info('Included router to app.')

if __name__ == "__main__":
    logger.info('Starting application...')
    uvicorn.run("api:app", port=8080, log_level="info")


