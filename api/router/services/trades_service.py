
from sqlmodel import Session, select
from api.database.models import Trade


class TradesService:
    
    def __init__(self, session: Session):
        self.session=session

    def read_id(self,id:int):
       trade = self.session.get(Trade,id)
       return trade

    def read_run_number(self, backtest_run_number:int):
        trades = self.session.exec((select(Trade).where(Trade.run_number==backtest_run_number))).all()
        return trades

    def delete_id(self, id:int):
        trade = self.session.get(Trade,id)
        if trade:
            self.session.delete(trade)
            self.session.commit()  
            return True
        return False 

    def delete_run_number(self, backtest_run_number:int):
        trades = self.session.exec(select(Trade).where(Trade.run_number==backtest_run_number)).all()
        if trades: 
            for trade in trades:
                self.session.delete(trade)
            self.session.commit()  
            return True
        return False