from fastapi import FastAPI
from app.routes.transform_route import router as transform_router
import logging
from app.config.constants import LOG_FILE

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Data Transformation API", version="1.0")

# Include transform route
app.include_router(transform_router, prefix="/api")

@app.get("/")
def home():
    return {"message": "Welcome to Data Transformation API"}
