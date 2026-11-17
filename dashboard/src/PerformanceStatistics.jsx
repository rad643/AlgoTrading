function PerformanceStatistics( {finalEquity,totalNetProfit,returnPct,sharpeRatio,annualizedPct,mdd,calmarRatio,totalTrades,winningTrades,losingTrades,winRate,profitFactor,expectancy,averageWin,averageLoss,payoffRatio,startingCash,totalCommission,totalSlippageCost} ) {
    return(
        <>

        <div className="performance-statistics-panel">
            <h2>Performance Statistics</h2>

            <section className="stats-section">
                
                <h3>Key Results</h3>
                <div className="stats-row">
                    <span className="stats-label">Final Equity</span>
                    <span className="stats-value">
                        { typeof finalEquity === "number"
                            ? finalEquity.toLocaleString("en-US", { style: "currency", currency: "USD" })
                            : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Total Net Profit</span>
                    <span className={ typeof totalNetProfit === "number"
                                        ? `stats-value ${totalNetProfit >= 0 ? "profit" : "loss"}`
                                        : "stats-value" }>
                        { typeof totalNetProfit === "number"
                            ? totalNetProfit.toLocaleString("en-US", { style: "currency", currency: "USD" })
                            : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Return %</span>
                    <span className={ typeof returnPct === "number"
                                        ? `stats-value ${returnPct >= 0 ? "profit" : "loss"}`
                                        : "stats-value" }>
                        { typeof returnPct === "number"
                            ? `${returnPct >= 0 ? "+" : ""}${returnPct.toFixed(2)}%`
                            : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Annualized Return</span>
                    <span className="stats-value">
                        { typeof annualizedPct === "number" ? `${annualizedPct.toFixed(2)}%` : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Sharpe Ratio</span>
                    <span className="stats-value">
                        { typeof sharpeRatio === "number" ? sharpeRatio.toFixed(2) : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Max Drawdown</span>
                    <span className={ typeof mdd === "number" ? "stats-value loss" : "stats-value" }>
                        { typeof mdd === "number" ? `-${Math.abs(mdd).toFixed(2)}%` : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Calmar Ratio</span>
                    <span className="stats-value">
                        { typeof calmarRatio === "number" ? calmarRatio.toFixed(2) : "—" }
                    </span>
                </div>
            </section>

            <section className="stats-section">
                <h3>Trading Statistics</h3>
                <div className="stats-row">
                    <span className="stats-label">Total Trades</span>
                    <span className="stats-value">
                        { typeof totalTrades === "number" ? totalTrades : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Winning Trades</span>
                    <span className="stats-value">
                        { typeof winningTrades === "number" ? winningTrades : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Losing Trades</span>
                    <span className="stats-value">
                        { typeof losingTrades === "number" ? losingTrades : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Win Rate</span>
                    <span className="stats-value">
                        { typeof winRate === "number" ? `${winRate.toFixed(1)}%` : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Profit Factor</span>
                    <span className="stats-value">
                        { typeof profitFactor === "number" ? profitFactor.toFixed(2) : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Expectancy (per trade)</span>
                    <span className="stats-value">
                        { typeof expectancy === "number"
                            ? expectancy.toLocaleString("en-US", { style: "currency", currency: "USD" })
                            : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Average Win</span>
                    <span className="stats-value">
                        { typeof averageWin === "number"
                            ? averageWin.toLocaleString("en-US", { style: "currency", currency: "USD" })
                            : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Average Loss</span>
                    <span className="stats-value">
                        { typeof averageLoss === "number"
                            ? averageLoss.toLocaleString("en-US", { style: "currency", currency: "USD" })
                            : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Payoff Ratio</span>
                    <span className="stats-value">
                        { typeof payoffRatio === "number" ? payoffRatio.toFixed(2) : "—" }
                    </span>
                </div>
            </section>

            <section className="stats-section">
                <h3>Other</h3>
                <div className="stats-row">
                    <span className="stats-label">Initial Cash</span>
                    <span className="stats-value">
                        { typeof startingCash === "number"
                            ? startingCash.toLocaleString("en-US", { style: "currency", currency: "USD" })
                            : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Total Commission</span>
                    <span className="stats-value">
                        { typeof totalCommission === "number"
                            ? totalCommission.toLocaleString("en-US", { style: "currency", currency: "USD" })
                            : "—" }
                    </span>
                </div>
                <div className="stats-row">
                    <span className="stats-label">Total Slippage Cost</span>
                    <span className="stats-value">
                        { typeof totalSlippageCost === "number"
                            ? totalSlippageCost.toLocaleString("en-US", { style: "currency", currency: "USD" })
                            : "—" }
                    </span>
                </div>
            </section>

        </div>

        </>
    )
}


export default PerformanceStatistics