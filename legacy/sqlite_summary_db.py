import sqlite3
from typing import Any

import pandas as pd


class SummaryDatabase:
    def __init__(self, name: str):

        self.connection = sqlite3.connect("data/summary.db", check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.create_table(name)

    def create_table(self, name: str):

        self.cursor.execute(f"""
                            CREATE TABLE IF NOT EXISTS {name} (
                            id INTEGER PRIMARY KEY,
                            run_number INTEGER,
                            ticker TEXT,
                            strategy TEXT,
                            starting_cash REAL, 
                            total_net_profit REAL,
                            mdd REAL,
                            expectancy REAL,
                            payoff_ratio REAL,
                            profit_factor REAL,
                            sharpe_ratio REAL,
                            labels TEXT
                            )
                            """)

    def create_summary(self, df: pd.DataFrame) -> dict[str, Any]:

        self.cursor.execute(
            """ 
                            INSERT INTO summary
                            ( run_number, ticker, strategy, starting_cash, total_net_profit, mdd,
                            expectancy, payoff_ratio, profit_factor, sharpe_ratio, labels )
                            VALUES 
                            ( :run_number, :ticker, :strategy, :starting_cash, :total_net_profit, 
                            :mdd, :expectancy, :payoff_ratio, :profit_factor, :sharpe_ratio, :labels ) 
                            """,
            {**df},
        )

        self.connection.commit()

        self.cursor.execute("SELECT * FROM summary")
        summary_with_id = self.cursor.fetchall()
        summary_with_id = summary_with_id[0]

        return {
            "id": summary_with_id[0],
            "run_number": summary_with_id[1],
            "ticker": summary_with_id[2],
            "strategy": summary_with_id[3],
            "starting_cash": summary_with_id[4],
            "total_net_profit": summary_with_id[5],
            "mdd": summary_with_id[6],
            "expectancy": summary_with_id[7],
            "payoff_ratio": summary_with_id[8],
            "profit_factor": summary_with_id[9],
            "sharpe_ratio": summary_with_id[10],
            "labels": summary_with_id[11],
        }

    def read_summary(self, backtest_run_number, name) -> dict[str, Any] | None:

        self.cursor.execute(
            f"""
                            SELECT * FROM {name}
                            WHERE run_number=? 
                            """,
            (backtest_run_number,),
        )

        row = self.cursor.fetchone()

        return (
            {
                "id": row[0],
                "run_number": row[1],
                "ticker": row[2],
                "strategy": row[3],
                "starting_cash": row[4],
                "total_net_profit": row[5],
                "mdd": row[6],
                "expectancy": row[7],
                "payoff_ratio": row[8],
                "profit_factor": row[9],
                "sharpe_ratio": row[10],
                "labels": row[11],
            }
            if row
            else None
        )

    def delete_summary_run_number(self, backtest_run_number, name):

        self.cursor.execute(
            f"select * from {name} where run_number=?", (backtest_run_number,)
        )
        deleted_row = self.cursor.fetchone()

        self.cursor.execute(
            f""" DELETE FROM {name} 
                            WHERE run_number=?
                            """,
            (backtest_run_number,),
        )
        self.connection.commit()

        return (
            {
                "id": deleted_row[0],
                "run_number": deleted_row[1],
                "ticker": deleted_row[2],
                "strategy": deleted_row[3],
                "starting_cash": deleted_row[4],
                "total_net_profit": deleted_row[5],
                "mdd": deleted_row[6],
                "expectancy": deleted_row[7],
                "payoff_ratio": deleted_row[8],
                "profit_factor": deleted_row[9],
                "sharpe_ratio": deleted_row[10],
                "labels": deleted_row[11],
            }
            if deleted_row
            else None
        )

    def close(self):
        self.connection.close()
