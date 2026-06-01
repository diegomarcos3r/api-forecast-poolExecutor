from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager para gerenciar o ciclo de vida do ProcessPoolExecutor"""
    # Startup
    with ProcessPoolExecutor() as pool:
        app.state.pool_executor = pool
        print("✓ ProcessPoolExecutor inicializado")
        yield
    # Shutdown
    print("✓ ProcessPoolExecutor finalizado")
