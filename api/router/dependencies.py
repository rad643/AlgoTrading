from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from api.database.session import get_session
from api.router.services.log_events_service import LogEventsService
from api.router.services.summary_service import SummaryService
from api.router.services.trades_service import TradesService

SessionDep=Annotated [Session, Depends(get_session)]

def get_summary_service(session: SessionDep):
    return SummaryService(session)

SummaryServiceDep= Annotated[ SummaryService, Depends(get_summary_service) ]

def get_log_events_service(session: SessionDep):
    return LogEventsService(session)

LogEventsServiceDep= Annotated[ LogEventsService, Depends(get_log_events_service) ]

def get_trades_service(session: SessionDep):
    return TradesService(session)

TradesServiceDep= Annotated[ TradesService, Depends(get_trades_service) ]