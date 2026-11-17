import { useState } from "react";



function Summary ( {summaries, fetchLogEvents, fetchTrades, fetchEquities, fetchDrawdowns, fetchPrices,
	fetchFinalEquity, fetchTotalNetProfit, fetchReturnPct, fetchSharpeRatio, fetchAnnualizedPct,fetchMdd,fetchCalmarRatio,
	fetchTotalTrades, fetchWinningTrades, fetchLosingTrades, fetchWinRate, fetchProfitFactor, fetchExpectancy, fetchAverageWin, fetchAverageLoss, fetchPayoffRatio, fetchStartingCash, fetchTotalCommission, fetchTotalSlippageCost
} ) {

		const [selectedTicker,setTicker]=useState("");

		const filteredItems= summaries.filter( (item) => {
			return(
				item.ticker.includes(selectedTicker)
			)
		});

    return(

			<> 

				<div className="result_summary">
					<h1>Summary results</h1>

					<input
						type="text"
						placeholder="Filter by ticker"
						value={selectedTicker}
						onChange={ (event) => setTicker(event.target.value) }
					/>

					<Table filteredItems={filteredItems}
						   fetchLogEvents={fetchLogEvents}
						   fetchTrades={fetchTrades}
						   fetchEquities={fetchEquities}
						   fetchDrawdowns={fetchDrawdowns}
					   fetchPrices={fetchPrices}
					   fetchFinalEquity={fetchFinalEquity}
					   fetchTotalNetProfit={fetchTotalNetProfit}
					   fetchReturnPct={fetchReturnPct}
					   fetchSharpeRatio={fetchSharpeRatio}
					   fetchAnnualizedPct={fetchAnnualizedPct}
					   fetchMdd={fetchMdd}
					   fetchCalmarRatio={fetchCalmarRatio}
					   fetchTotalTrades={fetchTotalTrades}
					   fetchWinningTrades={fetchWinningTrades}
					   fetchLosingTrades={fetchLosingTrades}
					   fetchWinRate={fetchWinRate}
					   fetchProfitFactor={fetchProfitFactor}
					   fetchExpectancy={fetchExpectancy}
					   fetchAverageWin={fetchAverageWin}
					   fetchAverageLoss={fetchAverageLoss}
					   fetchPayoffRatio={fetchPayoffRatio}
					   fetchStartingCash={fetchStartingCash}
					   fetchTotalCommission={fetchTotalCommission}
					   fetchTotalSlippageCost={fetchTotalSlippageCost}
					/>

				</div>

			</>

    );

}



function Table( {filteredItems, fetchLogEvents, fetchTrades, fetchEquities, fetchDrawdowns, fetchPrices, 
	fetchFinalEquity, fetchTotalNetProfit,fetchReturnPct, fetchSharpeRatio, fetchAnnualizedPct,fetchMdd,fetchCalmarRatio,
	fetchTotalTrades, fetchWinningTrades, fetchLosingTrades, fetchWinRate, fetchProfitFactor, fetchExpectancy, fetchAverageWin, fetchAverageLoss, fetchPayoffRatio, fetchStartingCash, fetchTotalCommission, fetchTotalSlippageCost
} ){

	return(
		<div>

			<table className="summary-table">
				<thead>
					<tr>

						<th>id</th>
						<th>ticker</th>
						<th>strategy</th>
						<th>starting cash</th>
						<th>total net profit</th>
						<th>mdd</th>
						<th>expectancy</th>
						<th>payoff ratio</th>
						<th>profit factor</th>
						<th>sharpe ratio</th>
						<th>labels</th>

					</tr>
				</thead>

				<tbody>
					{
						filteredItems.map( (summaryRow, indexRow) => {
							return (
								<tr key={summaryRow.id}
										onClick={ () => {
											fetchLogEvents(summaryRow, indexRow);
											fetchTrades(summaryRow, indexRow);
											fetchEquities(summaryRow);
											fetchDrawdowns(summaryRow);
											fetchPrices(summaryRow);
											fetchFinalEquity(summaryRow);
											fetchTotalNetProfit(summaryRow);
											fetchReturnPct(summaryRow)
											fetchSharpeRatio(summaryRow)
											fetchAnnualizedPct(summaryRow)
											fetchMdd(summaryRow)
											fetchCalmarRatio(summaryRow)
											fetchTotalTrades(summaryRow)
											fetchWinningTrades(summaryRow)
											fetchLosingTrades(summaryRow)
											fetchWinRate(summaryRow)
											fetchProfitFactor(summaryRow)
											fetchExpectancy(summaryRow)
											fetchAverageWin(summaryRow)
											fetchAverageLoss(summaryRow)
											fetchPayoffRatio(summaryRow)
											fetchStartingCash(summaryRow)
											fetchTotalCommission(summaryRow)
											fetchTotalSlippageCost(summaryRow)
										} }
								>

									<td>{indexRow+1}</td>
									<td>{summaryRow.ticker}</td>
									<td>{summaryRow.strategy}</td>
									<td>{summaryRow.starting_cash}</td>
									<td className={summaryRow.total_net_profit < 0 ? "loss" : summaryRow.total_net_profit > 0 ? "profit" : ""}>{summaryRow.total_net_profit}</td>
									<td>{summaryRow.mdd}</td>
									<td>{summaryRow.expectancy}</td>
									<td>{summaryRow.payoff_ratio}</td>
									<td>{summaryRow.profit_factor}</td>
									<td>{summaryRow.sharpe_ratio}</td>
									<td>{summaryRow.labels}</td>

								</tr>
							)
						})
					}
				</tbody>

			</table>
			
		</div>
	);

}




export default Summary