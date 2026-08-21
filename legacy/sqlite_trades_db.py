import sqlite3
from typing import Any

import pandas as pd


class TradesDatabase:
    def __init__(self, name: str):

        self.connection = sqlite3.connect("data/trades.db", check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table(name)

    def create_table(self, name: str):

        self.cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS {name} (
                            id INTEGER PRIMARY KEY,
                            run_number INTEGER,
                            ticker TEXT,
                            strategy TEXT,
                            entry_day INTEGER,
                            entry_price REAL,
                            exit_day INTEGER,
                            exit_price REAL,
                            profit REAL,
                            return_pct REAL,
                            labels TEXT,
                            number_trades_took_place INTEGER
                            )
                            """)

    def create_trade(self, df: pd.DataFrame) -> list[dict[str, Any]]:

        for event in df:
            self.cursor.execute(
                """ 
                                INSERT INTO trades
                                ( run_number, ticker, strategy, entry_day, entry_price, exit_day,
                                exit_price, profit, return_pct, labels, number_trades_took_place )           
                                VALUES 
                                ( :run_number, :ticker, :strategy, :entry_day, :entry_price, :exit_day,
                                :exit_price, :profit, :return_pct, :labels, :number_trades_took_place ) 
                                """,
                {
                    **event  # type: ignore[dict-item]
                },
            )

            self.connection.commit()

        self.cursor.execute("SELECT * FROM trades")
        list_trades = self.cursor.fetchall()
        events = []
        for event in list_trades:
            one_event = {
                "id": event[0],
                "run_number": event[1],
                "ticker": event[2],
                "strategy": event[3],
                "entry_day": event[4],
                "entry_price": event[5],
                "exit_day": event[6],
                "exit_price": event[7],
                "profit": event[8],
                "return_pct": event[9],
                "labels": event[10],
                "number_trades_took_place": event[11],
            }
            events.append(one_event)

        return events

    def read_trade(self, backtest_run_number, name) -> list[dict[Any, Any] | None]:

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
            results.append(row)
        return results

    def read_trade_id(self, backtest_run_number, name, id):

        events = self.read_trade(backtest_run_number, name)
        for event in events:
            if event["id"] == id:
                return event
        return None

    def delete_trade_run_number(self, backtest_run_number, name):

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
