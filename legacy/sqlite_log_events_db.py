import sqlite3
from typing import Any

import pandas as pd


class LogEventsDatabase:
    def __init__(self, name: str):

        self.connection = sqlite3.connect("data/log_events.db", check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table(name)

    def create_table(self, name: str):

        self.cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS {name} (
                            id INTEGER PRIMARY KEY,
                            run_number INTEGER,
                            day INTEGER,
                            date TEXT,
                            ticker TEXT,
                            strategy TEXT,
                            event_type TEXT,
                            message TEXT,
                            cash REAL,
                            equity REAL,
                            position INTEGER,
                            execution_price REAL,
                            pnl REAL,
                            labels TEXT
                            )
                            """)

    def create_event(self, df: pd.DataFrame) -> list[dict[str, Any]]:

        for event in df:
            self.cursor.execute(
                """ 
                                INSERT INTO log_events
                                ( run_number, day, date, ticker, strategy, event_type,
                                message, cash, equity, position, execution_price, pnl, labels )           
                                VALUES 
                                ( :run_number, :day, :date, :ticker, :strategy, :event_type, 
                                :message, :cash, :equity, :position, :execution_price, :pnl, :labels ) 
                                """,
                {
                    **event  # type: ignore [dict-item]
                },
            )

            self.connection.commit()

        self.cursor.execute("SELECT * FROM log_events")
        list_log_events = self.cursor.fetchall()
        events = []
        for event in list_log_events:
            one_event = {
                "id": event[0],
                "run_number": event[1],
                "day": event[2],
                "date": event[3],
                "ticker": event[4],
                "strategy": event[5],
                "event_type": event[6],
                "message": event[7],
                "cash": event[8],
                "equity": event[9],
                "position": event[10],
                "execution_price": event[11],
                "pnl": event[12],
                "labels": event[13],
            }
            events.append(one_event)

        return events

    def read_event(self, backtest_run_number, name) -> list[dict[Any, Any] | None]:

        self.cursor.execute(
            f"""
                            SELECT * FROM {name}
                            WHERE run_number=? 
                            """,
            (backtest_run_number,),
        )

        rows = self.cursor.fetchall()
        results = []

        for row in rows:
            row = (
                {
                    "id": row[0],
                    "run_number": row[1],
                    "day": row[2],
                    "date": row[3],
                    "ticker": row[4],
                    "strategy": row[5],
                    "row_type": row[6],
                    "message": row[7],
                    "cash": row[8],
                    "equity": row[9],
                    "position": row[10],
                    "execution_price": row[11],
                    "pnl": row[12],
                    "labels": row[13],
                }
                if row
                else None
            )
            results.append(row)
        return results

    def read_event_id(self, backtest_run_number, name, id):

        events = self.read_event(backtest_run_number, name)
        for event in events:
            if event["id"] == id:
                return event
        return None

    def delete_log_event_run_number(self, backtest_run_number, name):

        self.cursor.execute(
            f"select * from {name} where run_number=?", (backtest_run_number,)
        )
        rows = self.cursor.fetchall()

        self.cursor.execute(
            f"delete from {name} where run_number=?", (backtest_run_number,)
        )
        self.connection.commit()

        deleted_rows = []
        for row in rows:
            row = (
                {
                    "id": row[0],
                    "run_number": row[1],
                    "ticker": row[2],
                    "strategy": row[3],
                    "entry_day": row[4],
                    "entry_price": row[5],
                    "exit_day": row[6],
                    "exit_price": row[7],
                    "profit": row[8],
                    "return_pct": row[9],
                    "labels": row[10],
                    "number_trades_took_place": row[11],
                }
                if row
                else None
            )
            deleted_rows.append(row)
        return deleted_rows

    def close(self):
        self.connection.close()
