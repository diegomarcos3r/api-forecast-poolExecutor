from fastapi import FastAPI
from forecast_routes import forecast_router
from config import lifespan


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "API de Forecast - Use POST /forecast/run-forecast"}


app.include_router(forecast_router)