import uvicorn
from fastapi import FastAPI

from routers.wpp_router import router


app = FastAPI(title="Test Task", debug=True)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("api:app", port=8080, log_level="info")


