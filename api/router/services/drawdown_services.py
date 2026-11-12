from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database.models import Drawdowns


class DrawdownsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_id(self, id: int):
        drawdowns = await self.session.get(Drawdowns, id)
        return drawdowns

    async def read_run_number(self, backtest_run_number: int):
        result = await self.session.exec(
            select(Drawdowns)
            .where(Drawdowns.run_number == backtest_run_number)
            .order_by(col(Drawdowns.day).asc())
        )
        drawdowns = result.all()
        return drawdowns

    async def delete_id(self, id: int):
        drawdown = await self.session.get(Drawdowns, id)
        if drawdown:
            await self.session.delete(drawdown)
            await self.session.commit()
            return True
        return False

    async def delete_run_number(self, backtest_run_number: int):
        result = await self.session.exec(
            select(Drawdowns).where(Drawdowns.run_number == backtest_run_number)
        )
        drawdowns = result.all()
        if drawdowns:
            for drawdown in drawdowns:
                await self.session.delete(drawdown)
            await self.session.commit()
            return True
        return False
