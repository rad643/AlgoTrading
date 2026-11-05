function LogEvents( {logEvents, logEventRowRunNumber} ){

    return(
        <>

        <div className="result_summary">
					<h1>Log Events</h1>

					<Table logEvents={logEvents}
								 logEventRowRunNumber={logEventRowRunNumber}
					/>

				</div>

        </>
    )
}



function Table( {logEvents, logEventRowRunNumber} ){

	return(
		<div>

			<table className="log-table">
				<thead>
					<tr>

						<th>id</th>
						<th>run_number</th>
						<th>day</th>
						<th>date</th>
						<th>ticker</th>
						<th>strategy</th>
						<th>event_type</th>
						<th>message</th>
						<th>cash</th>
						<th>equity</th>
						<th>position</th>
						<th>execution_price</th>
						<th>pnl</th>
						<th>labels</th>

					</tr>
				</thead>

				<tbody>
					{
						logEvents.map( (logEventRow, indexRow) => {
							return (
								<tr key={logEventRow.id}>

									<td>{indexRow+1}</td>
									<td>{logEventRowRunNumber}</td>
									<td>{logEventRow.day}</td>
									<td>{logEventRow.date}</td>
									<td>{logEventRow.ticker}</td>
									<td>{logEventRow.strategy}</td>
									<td>{logEventRow.event_type}</td>
									<td>{logEventRow.message}</td>
									<td>{logEventRow.cash}</td>
									<td>{logEventRow.equity}</td>
									<td>{logEventRow.position}</td>
									<td>{logEventRow.execution_price}</td>
									<td className={logEventRow.pnl < 0 ? "loss" : logEventRow.pnl > 0 ? "profit" : ""}>{logEventRow.pnl}</td>
									<td>{logEventRow.labels}</td>

								</tr>
							)
						})
					}
				</tbody>

			</table>
			
		</div>
	);

}


export default LogEvents