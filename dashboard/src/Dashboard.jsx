import { useState, useEffect } from "react";
import Summary from "./Summary";
import LogEvents from "./LogEvents";
import Trades from "./Trades"; 
import Equities from "./EquityCurve";
import Drawdowns from "./DrawdownSeriesChart";
import Prices from "./PriceChart";
import BacktestParameters from "./BacktestParameters";


export default function Dashboard() { 

    const [summaries,setSummaries] = useState([]);
		const [logEvents,setLogEvents] = useState([]);
		const [trades,setTrades] = useState([]);
		const [equities, setEquities] = useState([]);
		const [drawdowns, setDrawdowns] = useState([]);
		const [prices, setPrices] = useState([]);
    const [error,setError] = useState("");
    const [loading,setLoading] = useState(true);
		const [logEventRowRunNumber, setlogEventRowRunNumber] = useState(0)
		const [tradeRowRunNumber, setTradeRowRunNumber] = useState(0)

    async function fetchSummaries() {

			const url = `http://localhost:8000/summary`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setSummaries(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		async function fetchLogEvents(summaryRow, indexRow) {

			const url = `http://localhost:8000/log_events_backtest_run_number/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setLogEvents(result)
				setlogEventRowRunNumber(indexRow+1)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		async function fetchTrades(summaryRow, indexRow) {

			const url = `http://localhost:8000/trades_backtest_run_number/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setTrades(result)
				setTradeRowRunNumber(indexRow+1)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		async function fetchEquities(summaryRow) {

			const url = `http://localhost:8000/equities_backtest_run_number/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setEquities(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		async function fetchDrawdowns(summaryRow) {

			const url = `http://localhost:8000/drawdowns_backtest_run_number/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setDrawdowns(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		async function fetchPrices(summaryRow) {

			const url = `http://localhost:8000/prices_backtest_run_number/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setPrices(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		useEffect( () => { fetchSummaries() } , [] );

		function clearSummaryRows() { 
			
			setSummaries( [] )
			setLogEvents( [] )
			setTrades( [] )
			setEquities( [] )
			setDrawdowns( [] )
			setPrices( [] )

		};

		function addRun(summaryRow) { 

			setSummaries( [...summaries , summaryRow] )

		};

		if (loading) return <p>Loading...</p>;
  	if (error) return <p>A network error was encountered</p>;

    return(
        <>

				<div className="layout">

					<BacktestParameters clearSummaryRows={clearSummaryRows}
															addRun={addRun}
					/>

					<div className="results">
						<h1>Backtest results</h1>

						<Summary summaries={summaries}
										 fetchLogEvents={fetchLogEvents}
										 fetchTrades={fetchTrades}
										 fetchEquities={fetchEquities}
										 fetchDrawdowns={fetchDrawdowns}
										 fetchPrices={fetchPrices}
						/>
						<Prices prices={prices}
										trades={trades}
						/>
						<Equities equities={equities}
						/>
						<Drawdowns drawdowns={drawdowns}
						/>
						<LogEvents logEvents={logEvents}
											 logEventRowRunNumber={logEventRowRunNumber}
						/>
						<Trades trades={trades}
										tradeRowRunNumber={tradeRowRunNumber}
						/>

					</div>

				</div>

        </>
    )
}