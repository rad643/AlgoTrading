function Trades( {trades, tradeRowRunNumber} ){
    return(
        <>

        <div className="result_summary">
            <h1>Trades</h1>

            <Table trades={trades}
                   tradeRowRunNumber={tradeRowRunNumber}
            />

        </div>

        </>
    )
}


function Table( {trades, tradeRowRunNumber} ){

	return(
		<div>

			<table className="trades-table">
				<thead>
					<tr>

						<th>id</th>
						<th>run_number</th>
						<th>ticker</th>
						<th>strategy</th>
						<th>entry_day</th>
						<th>entry_price</th>
						<th>exit_day</th>
						<th>exit_price</th>
						<th>profit</th>
						<th>return_pct</th>
						<th>labels</th>
						<th>number_trades_took_place</th>

					</tr>
				</thead>

				<tbody>
					{
						trades.map( (tradeRow, indexRow) => {
							return (
								<tr key={tradeRow.id}>

									<td>{indexRow+1}</td>
									<td>{tradeRowRunNumber}</td>
									<td>{tradeRow.ticker}</td>
									<td>{tradeRow.strategy}</td>
									<td>{tradeRow.entry_day}</td>
									<td>{tradeRow.entry_price}</td>
									<td>{tradeRow.exit_day}</td>
									<td>{tradeRow.exit_price}</td>
									<td className={tradeRow.profit < 0 ? "loss" : tradeRow.profit > 0 ? "profit" : ""}>{tradeRow.profit}</td>
									<td className={tradeRow.return_pct < 0 ? "loss" : tradeRow.return_pct > 0 ? "profit" : ""}>{tradeRow.return_pct}</td>
									<td>{tradeRow.labels}</td>
									<td>{tradeRow.number_trades_took_place}</td>

								</tr>
							)
						})
					}
				</tbody>

			</table>
			
		</div>
	);

}


export default Trades