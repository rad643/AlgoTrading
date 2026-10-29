import { useEffect, useState } from "react";

function Button( { text="▶ Run backtest"} ) {

  return (
    <button>{text}</button>
  );
}



function Table(props){

	return(
		<div>
			<table>
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
						props.attributes.map( (item) => {
							return (
								<tr key={item.id}>
									<td>{item.id}</td>
									<td>{item.ticker}</td>
									<td>{item.strategy}</td>
									<td>{item.starting_cash}</td>
									<td>{item.total_net_profit}</td>
									<td>{item.mdd}</td>
									<td>{item.expectancy}</td>
									<td>{item.payoff_ratio}</td>
									<td>{item.profit_factor}</td>
									<td>{item.sharpe_ratio}</td>
									<td>{item.labels}</td>
								</tr>
							)
						})
					}
				</tbody>
			</table>
		</div>
	);

}




function Summary () {

		const [ticker,setTicker]=useState("");
		const [data,setData] = useState([]);
		const [error,setError] = useState("");
		const [loading,setLoading] = useState(true);

		const divStyle={ display: "flex", justifyContent: "space-between", alignItems: "center" }

		useEffect( () => {
		
			fetch("http://localhost:8000/summary")

				.then( (response) => {
					if (response.status >= 400) {
						throw new Error("server error");
					}
					return response.json();
				} )

				.then( (response) => setData( response ) )

				.catch( (error) => setError(error) )

				.finally( () => setLoading(false) );
			
		}, [] );

		if (loading) return <p>Loading...</p>;
  
  	if (error) return <p>A network error was encountered</p>;

		const filteredItems= data.filter( (item) => {
			return(
				item.ticker.includes(ticker)
			)
		})

    return(
			<>

			<div style={divStyle}>
				<h1>Backtest results</h1>
				<Button />
			</div>
			<input 
				type="text"
				placeholder="Filter by ticker"
				value={ticker}
				onChange={ (event) => setTicker(event.target.value) }
			/>
			<Table attributes={filteredItems}/>
		
			</>
    );

}

export default Summary




