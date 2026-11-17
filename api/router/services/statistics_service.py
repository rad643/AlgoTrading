from sqlmodel import col, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database.models import Equities, Summary, Trade


class StatisticsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def final_equity(self, id: int):
        final_equity = await self.session.exec(
            select(
                (col(Summary.starting_cash) + col(Summary.total_net_profit)).label(
                    "final_equity"
                )
            ).where(Summary.id == id)
        )
        return final_equity.first()

    async def total_net_profit(self, id: int):
        total_net_profit = await self.session.exec(
            select(Summary.total_net_profit).where(Summary.id == id)
        )
        return total_net_profit.first()

    async def return_pct(self, id: int):
        return_pct = await self.session.exec(
            select((Summary.total_net_profit / Summary.starting_cash) * 100).where(
                Summary.id == id
            )
        )
        return return_pct.first()

    async def sharpe_ratio(self, id: int):
        sharpe_ratio = await self.session.exec(
            select(Summary.sharpe_ratio).where(Summary.id == id)
        )
        return sharpe_ratio.first()

    async def annualized_pct(self, id: int):
        MARKET_DAYS_PER_YEAR = (
            252  # number of days the US stock market is open in a year (constant)
        )
        final_equity = await self.final_equity(id)
        if final_equity is None:
            return None
        starting_cash = (
            await self.session.exec(
                select(Summary.starting_cash).where(Summary.id == id)
            )
        ).first()
        days_in_run = (
            await self.session.exec(
                select(func.count(col(Equities.day))).where(Equities.run_number == id)
            )
        ).first()
        if days_in_run is None:
            return None
        annualized_pct = (
            (final_equity / starting_cash) ** (MARKET_DAYS_PER_YEAR / days_in_run) - 1
        ) * 100
        return annualized_pct

    async def mdd(self, id: int):
        mdd = await self.session.exec(select(Summary.mdd).where(Summary.id == id))
        return mdd.first()

    async def calmar_ratio(self, id: int):
        annualized_pct = await self.annualized_pct(id)
        if annualized_pct is None:
            return None
        mdd = await self.mdd(id)
        if mdd == 0:
            return None
        calmar_ratio = annualized_pct / mdd
        return calmar_ratio

    async def total_trades(self, id: int):
        total_trades = (
            await self.session.exec(
                select(func.count(col(Trade.id))).where(Trade.run_number == id)
            )
        ).first()
        if total_trades is None:
            return None
        return total_trades

    async def winning_trades(self, id: int):
        winning_trades = await self.session.exec(
            (select(func.count(col(Trade.id))).where(Trade.run_number == id)).where(
                Trade.profit > 0
            )
        )
        if winning_trades is None:
            return None
        return winning_trades.first()

    async def losing_trades(self, id: int):
        losing_trades = await self.session.exec(
            (select(func.count(col(Trade.id))).where(Trade.run_number == id)).where(
                Trade.profit < 0
            )
        )
        if losing_trades is None:
            return None
        return losing_trades.first()

    async def win_rate(self, id: int):
        # count() returns 0, not None, for an unknown id, so check the run exists via its summary row
        if await self.final_equity(id) is None:
            return None
        total_trades = await self.total_trades(id)
        if total_trades == 0:
            return 0.0
        winning_trades = await self.winning_trades(id)
        win_rate = (winning_trades / total_trades) * 100
        return win_rate

    async def profit_factor(self, id: int):
        profit_factor = await self.session.exec(
            select(Summary.profit_factor).where(Summary.id == id)
        )
        return profit_factor.first()

    async def expectancy(self, id: int):
        expectancy = await self.session.exec(
            select(Summary.expectancy).where(Summary.id == id)
        )
        return expectancy.first()

    async def average_win(self, id: int):
        if await self.final_equity(id) is None:
            return None
        sum_winning_trades = (
            await self.session.exec(
                select(func.sum(Trade.profit))
                .where(Trade.run_number == id)
                .where(Trade.profit > 0)
            )
        ).first()
        nb_winning_trades = await self.winning_trades(id)
        if nb_winning_trades == 0:
            return 0.0
        average_win = sum_winning_trades / nb_winning_trades
        return average_win

    async def average_loss(self, id: int):
        if await self.final_equity(id) is None:
            return None
        sum_losing_trades = (
            await self.session.exec(
                select(func.sum(Trade.profit))
                .where(Trade.run_number == id)
                .where(Trade.profit < 0)
            )
        ).first()
        nb_losing_trades = await self.losing_trades(id)
        if nb_losing_trades == 0:
            return 0.0
        average_loss = sum_losing_trades / nb_losing_trades
        return average_loss

    async def payoff_ratio(self, id: int):
        payoff_ratio = await self.session.exec(
            select(Summary.payoff_ratio).where(Summary.id == id)
        )
        return payoff_ratio.first()

    async def starting_cash(self, id: int):
        starting_cash = await self.session.exec(
            select(Summary.starting_cash).where(Summary.id == id)
        )
        return starting_cash.first()

    async def total_commission(self, id: int):
        # sum() returns None, not 0, for a run with no trades, so check the run exists via its summary row
        if await self.final_equity(id) is None:
            return None
        total_commission = (
            await self.session.exec(
                select(func.sum(Trade.commission)).where(Trade.run_number == id)
            )
        ).first()
        if total_commission is None:
            return 0.0
        return total_commission

    async def total_slippage_cost(self, id: int):
        if await self.final_equity(id) is None:
            return None
        total_slippage_cost = (
            await self.session.exec(
                select(func.sum(Trade.slippage_cost)).where(Trade.run_number == id)
            )
        ).first()
        if total_slippage_cost is None:
            return 0.0
        return total_slippage_cost
