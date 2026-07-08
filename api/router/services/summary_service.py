from sqlmodel import Session, select
from api.database.models import Summary


class SummaryService:

    def __init__(self, session: Session):
        self.session=session

    def read(self, backtest_run_number:int):
        summary = self.session.exec(select(Summary).where(Summary.run_number==backtest_run_number)).first()
        return summary

    def delete(self, backtest_run_number:int): 
       summary = self.session.exec(select(Summary).where(Summary.run_number==backtest_run_number)).first()
       if summary:
           self.session.delete(summary)
           self.session.commit()
           return True
       return False