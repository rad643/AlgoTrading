from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database.models import LogEvent


class LogEventsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_id(self, id: int):
        log_event = await self.session.get(LogEvent, id)
        return log_event

    async def read_run_number(self, backtest_run_number: int):
        result = await self.session.exec(
            select(LogEvent).where(LogEvent.run_number == backtest_run_number)
        )
        log_events = result.all()
        return log_events

    async def delete_id(self, id: int):
        log_event = await self.session.get(LogEvent, id)
        if log_event:
            await self.session.delete(log_event)
            await self.session.commit()
            return True
        return False

    async def delete_run_number(self, backtest_run_number: int):
        result = await self.session.exec(
            select(LogEvent).where(LogEvent.run_number == backtest_run_number)
        )
        log_events = result.all()
        if log_events:
            for event in log_events:
                await self.session.delete(event)
            await self.session.commit()
            return True
        return False
