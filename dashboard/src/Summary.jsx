import { useState } from "react";



function Summary ( {summaries, fetchLogEvents, fetchTrades} ) {

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
					/>

				</div>

			</>

    );

}



function Table( {filteredItems, fetchLogEvents, fetchTrades} ){

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