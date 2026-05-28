import asyncio
from fastapi import APIRouter, Request
from models.models import CreateSimulation
from services.forecast import Forecast


forecast_router = APIRouter(prefix="/forecast", tags=["forecast"])


@forecast_router.post("/run-forecast")
async def create_simulation(request: Request, new_simulation: CreateSimulation) -> dict:
    
    forecast = Forecast(
        nr_simulations=new_simulation.nr_simulations,
        backlog_min=new_simulation.backlog_min,
        backlog_max=new_simulation.backlog_max,
        throughput=new_simulation.throughput
    )

    # Usar o pool executor do app.state
    loop = asyncio.get_running_loop()
    pool_executor = request.app.state.pool_executor
    result = await loop.run_in_executor(pool_executor, forecast.run_forecast)

    return result


@forecast_router.get("/")
async def health_check() -> dict:
    return {"status": "API de Forecast rodando"}
