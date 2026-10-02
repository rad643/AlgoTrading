from sqlmodel.ext.asyncio.session import AsyncSession

from api.database.models import Summary


class SummaryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read(self, id: int):
        summary = await self.session.get(Summary, id)
        return summary

    async def delete(self, id: int):
        summary = await self.session.get(Summary, id)
        if summary:
            await self.session.delete(summary)
            await self.session.commit()
            return True
        return False
