from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from api.database.session import get_session
from api.router.services.drawdown_services import DrawdownsService
from api.router.services.equities_service import EquitiesService
from api.router.services.log_events_service import LogEventsService
from api.router.services.prices_service import PricesService
from api.router.services.statistics_service import StatisticsService
from api.router.services.summary_service import SummaryService
from api.router.services.trades_service import TradesService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_summary_service(session: SessionDep):
    return SummaryService(session)


SummaryServiceDep = Annotated[SummaryService, Depends(get_summary_service)]


def get_log_events_service(session: SessionDep):
    return LogEventsService(session)


LogEventsServiceDep = Annotated[LogEventsService, Depends(get_log_events_service)]


def get_trades_service(session: SessionDep):
    return TradesService(session)


TradesServiceDep = Annotated[TradesService, Depends(get_trades_service)]


def get_equities_service(session: SessionDep):
    return EquitiesService(session)


EquitiesServiceDep = Annotated[EquitiesService, Depends(get_equities_service)]


def get_drawdowns_service(session: SessionDep):
    return DrawdownsService(session)


DrawdownsServiceDep = Annotated[DrawdownsService, Depends(get_drawdowns_service)]


def get_prices_service(session: SessionDep):
    return PricesService(session)


PricesServiceDep = Annotated[PricesService, Depends(get_prices_service)]


def get_statistics_service(session: SessionDep):
    return StatisticsService(session)


StatisticsServiceDep = Annotated[StatisticsService, Depends(get_statistics_service)]
