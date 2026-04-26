from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.order_service.api.dependencies import get_catalog_client
from src.order_service.application.usecases.create_order import CreateOrderUseCase
from src.order_service.application.usecases.get_order import GetOrderUseCase
from src.order_service.core.exceptions import (
    CatalogServiceError,
    ItemNotAvailableError,
    OrderNotFoundError,
)
from src.order_service.infrastructure.clients.catalog import CatalogClient
from src.order_service.infrastructure.db.session import get_session
from src.order_service.infrastructure.repositories.orders import OrdersRepository
from src.order_service.schemas.orders import CreateOrderRequest, OrderResponse


router = APIRouter(prefix="/api/orders", tags=["orders"])


def build_order_response(order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        quantity=order.quantity,
        item_id=order.item_id,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
    data: CreateOrderRequest,
    session: AsyncSession = Depends(get_session),
    catalog_client: CatalogClient = Depends(get_catalog_client)
) -> OrderResponse:
    orders = OrdersRepository(session)
    usecase = CreateOrderUseCase(
        session=session,
        orders=orders,
        catalog_client=catalog_client,
    )

    try:
        order = await usecase.execute(
            user_id=data.user_id,
            item_id=data.item_id,
            quantity=data.quantity,
            idempotency_key=data.idempotency_key,
        )
    except ItemNotAvailableError as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))
    except CatalogServiceError as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc))

    return build_order_response(order)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    session: AsyncSession = Depends(get_session)
) -> OrderResponse:
    orders = OrdersRepository(session)
    usecase = GetOrderUseCase(orders=orders)

    try:
        order = await usecase.execute(order_id)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")

    return build_order_response(order)
