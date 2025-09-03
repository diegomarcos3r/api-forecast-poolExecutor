from fastapi import APIRouter
from models.models import CreateSimulation
from typing import Dict
from services.forecast import Forecast


# instanciar classe para criação da API

forecast_router = APIRouter(prefix="/forecast", tags=["forecast"])


# Endpoints

@forecast_router.post("/create-simulation")
async def create_simulation(new_simulation: CreateSimulation) -> dict:

    forecast = Forecast(
        nr_simulations = new_simulation.nr_simulations,
        backlog_min = new_simulation.backlog_min,
        backlog_max = new_simulation.backlog_max,
        throughput = new_simulation.throughput
    )

    # Rodar simulação

    forecast_weeks = forecast.run_simulation()

    # Gerar percentis

    percentiles = forecast.calculate_percentiles(forecast_weeks,[50,75,85,95])
    
    # Gerar resposta
    response = forecast.format_forecast_response(
        p50=percentiles[50],
        p75=percentiles[75],
        p85=percentiles[85],
        p95=percentiles[95]
        )

    return response
