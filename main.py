import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.order_service.api.routes.orders import router as orders_router
from src.order_service.application.usecases.run_outbox_worker import run_outbox_worker
from src.order_service.infrastructure.kafka.consumer import run_shipment_consumer


logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    stop_event = asyncio.Event()
    outbox_worker_task = asyncio.create_task(run_outbox_worker(stop_event))
    shipment_consumer_task = asyncio.create_task(run_shipment_consumer())

    try:
        yield
    finally:
        stop_event.set()
        shipment_consumer_task.cancel()

        try:
            await outbox_worker_task
        except Exception:
            logger.exception("Outbox worker stopped with error")

        try:
            await shipment_consumer_task
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Shipment consumer stopped with error")


app = FastAPI(title="Order_service", lifespan=lifespan)

app.include_router(orders_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
