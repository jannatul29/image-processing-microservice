from fastapi import FastAPI
from routers import upload, process
from fastapi import FastAPI

app = FastAPI(
    title="Image Processing API",
    description="API for handling high-dimensional TIFF images",
    version="1.0",
)

# Register routers
app.include_router(upload.router)
app.include_router(process.router)
