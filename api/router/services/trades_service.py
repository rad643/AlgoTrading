from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from api.database.models import Trade


class TradesService:
    
    def __init__(self, session: AsyncSession):
        self.session=session

    async def read_id(self,id:int):
       trade = await self.session.get(Trade,id)
       return trade

    async def read_run_number(self, backtest_run_number:int):
        result = await self.session.exec((select(Trade).where(Trade.run_number==backtest_run_number)))
        trades = result.all()
        return trades

    async def delete_id(self, id:int):
        trade = await self.session.get(Trade,id)
        if trade:
            await self.session.delete(trade)
            await self.session.commit()  
            return True
        return False 

    async def delete_run_number(self, backtest_run_number:int):
        result = await self.session.exec((select(Trade).where(Trade.run_number==backtest_run_number)))
        trades = result.all()
        if trades: 
            for trade in trades:
                await self.session.delete(trade)
            await self.session.commit()  
            return True
        return False