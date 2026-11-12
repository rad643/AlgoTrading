from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database.models import Equities


class EquitiesService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_id(self, id: int):
        equities = await self.session.get(Equities, id)
        return equities

    async def read_run_number(self, backtest_run_number: int):
        result = await self.session.exec(
            select(Equities)
            .where(Equities.run_number == backtest_run_number)
            .order_by(col(Equities.day).asc())
        )
        equities = result.all()
        return equities

    async def delete_id(self, id: int):
        equity = await self.session.get(Equities, id)
        if equity:
            await self.session.delete(equity)
            await self.session.commit()
            return True
        return False

    async def delete_run_number(self, backtest_run_number: int):
        result = await self.session.exec(
            select(Equities).where(Equities.run_number == backtest_run_number)
        )
        equities = result.all()
        if equities:
            for equity in equities:
                await self.session.delete(equity)
            await self.session.commit()
            return True
        return False
