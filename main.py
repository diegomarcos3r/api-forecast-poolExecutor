from fastapi import FastAPI
from forecast_routes import forecast_router

app = FastAPI()

app.include_router(forecast_router)