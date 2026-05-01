import asyncio

from src.order_service.infrastructure.clients.notifications import (
    NotificationsClient,
    NotificationsServiceError,
)


async def send_order_notifications(
    *,
    order_id: str,
    status: str,
    reason: str | None = None
) -> None:
    messages = {
        "NEW": "NEW: Ваш заказ создан и ожидает оплаты",
        "PAID": "PAID: Ваш заказ успешно оплачен и готов к отправке",
        "SHIPPED": "SHIPPED: Ваш заказ отправлен в доставку",
        "CANCELLED": f"CANCELLED: Ваш заказ отменен. Причина: {reason or 'не указана'}",
    }
    
    message = messages.get(status)
    if message is None:
        return
    
    client = NotificationsClient()
    
    for attempt in range(3):
        try:
            await client.send_notification(
                message=message,
                reference_id=order_id,
                idempotency_key=f"notification-{status.lower()}-{order_id}"
            )
            
            print(
                f"NOTIFICATION: sent for order={order_id} status={status}",
                flush=True,
            )
            return
        
        except NotificationsServiceError as exc:
            print(
                f"NOTIFICATION: failed attempt={attempt + 1} "
                f"for order={order_id} status={status}: {exc}",
                flush=True,
            )
            await asyncio.sleep(2)
