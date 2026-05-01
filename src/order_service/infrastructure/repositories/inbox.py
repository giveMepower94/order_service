from sqlalchemy.ext.asyncio import AsyncSession

from src.order_service.infrastructure.db.models import InboxMessageModel


class InboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, event_id: str) -> bool:
        message = await self.session.get(InboxMessageModel, event_id)
        return message is not None

    async def save_processed(
        self,
        *,
        event_id: str,
        event_type: str,
        payload: dict
    ):
        self.session.add(
            InboxMessageModel(
                id=event_id,
                event_type=event_type,
                payload=payload
            )
        )
        await self.session.flush()
