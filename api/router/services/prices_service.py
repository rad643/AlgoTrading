from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database.models import Prices


class PricesService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_id(self, id: int):
        price = await self.session.get(Prices, id)
        return price

    async def read_run_number(self, backtest_run_number: int):
        result = await self.session.exec(
            select(Prices)
            .where(Prices.run_number == backtest_run_number)
            .order_by(col(Prices.day).asc())
        )
        prices = result.all()
        return prices

    async def delete_id(self, id: int):
        price = await self.session.get(Prices, id)
        if price:
            await self.session.delete(price)
            await self.session.commit()
            return True
        return False

    async def delete_run_number(self, backtest_run_number: int):
        result = await self.session.exec(
            select(Prices).where(Prices.run_number == backtest_run_number)
        )
        prices = result.all()
        if prices:
            for price in prices:
                await self.session.delete(price)
            await self.session.commit()
            return True
        return False
