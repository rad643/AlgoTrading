
from sqlmodel import Session, select
from api.database.models import LogEvent



class LogEventsService:
    
    def __init__(self, session: Session):
        self.session=session

    def read_id(self,id:int):
        log_event = self.session.get(LogEvent,id)
        return log_event

    def read_run_number(self, backtest_run_number:int):
        log_events = self.session.exec((select(LogEvent).where(LogEvent.run_number==backtest_run_number))).all()
        return log_events

    def delete_id(self,id:int):
        log_event = self.session.get(LogEvent,id)
        if log_event:
            self.session.delete(log_event)
            self.session.commit()  
            return True
        return False 

    def delete_run_number(self, backtest_run_number:int):
        log_events = self.session.exec(select(LogEvent).where(LogEvent.run_number==backtest_run_number)).all()
        if log_events: 
            for event in log_events:
                self.session.delete(event)
            self.session.commit()  
            return True
        return False