from sqlmodel import select
from api.database.models import Summary
from sqlmodel.ext.asyncio.session import AsyncSession

class SummaryService:

    def __init__(self, session: AsyncSession):
        self.session=session

    async def read(self, backtest_run_number:int):
        result = await self.session.exec(select(Summary).where(Summary.run_number==backtest_run_number))
        summary = result.first()
        return summary

    async def delete(self, backtest_run_number:int): 
       result = await self.session.exec(select(Summary).where(Summary.run_number==backtest_run_number))
       summary = result.first()
       if summary:
           await self.session.delete(summary)
           await self.session.commit()
           return True
       return False