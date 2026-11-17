import { useState, useEffect } from "react";
import Summary from "./Summary";
import LogEvents from "./LogEvents";
import Trades from "./Trades"; 
import Equities from "./EquityCurve";
import Drawdowns from "./DrawdownSeriesChart";
import Prices from "./PriceChart";
import BacktestParameters from "./BacktestParameters";
import PerformanceStatistics from "./PerformanceStatistics";

export default function Dashboard() { 

    const [summaries,setSummaries] = useState([]);
		const [logEvents,setLogEvents] = useState([]);
		const [trades,setTrades] = useState([]);
		const [equities, setEquities] = useState([]);
		const [drawdowns, setDrawdowns] = useState([]);
		const [prices, setPrices] = useState([]);
		const [finalEquity, setFinalEquity] = useState([]);
		const [totalNetProfit, setTotalNetProfit] = useState([]);
		const [returnPct, setReturnPct] = useState([]);
		const [sharpeRatio, setSharpeRatio] = useState([]);
		const [annualizedPct, setAnnualizedPct] = useState([]);
		const [mdd, setMdd] = useState([]);
		const [calmarRatio, setCalmarRatio] = useState([]);
		const [totalTrades, setTotalTrades] = useState([]);
		const [winningTrades, setWinningTrades] = useState([]);
		const [losingTrades, setLosingTrades] = useState([]);
		const [winRate, setWinRate] = useState([]);
		const [profitFactor, setProfitFactor] = useState([]);
		const [expectancy, setExpectancy] = useState([]);
		const [averageWin, setAverageWin] = useState([]);
		const [averageLoss, setAverageLoss] = useState([]);
		const [payoffRatio, setPayoffRatio] = useState([]);
		const [startingCash, setStartingCash] = useState([]);
		const [totalCommission, setTotalCommission] = useState([]);
		const [totalSlippageCost, setTotalSlippageCost] = useState([]);
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

		async function fetchFinalEquity(summaryRow) {

			const url = `http://localhost:8000/final_equity/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setFinalEquity(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		async function fetchTotalNetProfit(summaryRow) {

			const url = `http://localhost:8000/total_net_profit/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setTotalNetProfit(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		async function fetchReturnPct(summaryRow) {

			const url = `http://localhost:8000/return_pct/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setReturnPct(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};
		
		async function fetchSharpeRatio(summaryRow) {

			const url = `http://localhost:8000/sharpe_ratio/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setSharpeRatio(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		async function fetchAnnualizedPct(summaryRow) {

			const url = `http://localhost:8000/annualized_pct/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setAnnualizedPct(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}
		
		};

		async function fetchMdd(summaryRow) {

			const url = `http://localhost:8000/maximum_drawdown/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json(); 
				setMdd(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchCalmarRatio(summaryRow) {

			const url = `http://localhost:8000/calmar_ratio/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setCalmarRatio(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchTotalTrades(summaryRow) {

			const url = `http://localhost:8000/total_trades/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setTotalTrades(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchWinningTrades(summaryRow) {

			const url = `http://localhost:8000/winning_trades/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setWinningTrades(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchLosingTrades(summaryRow) {

			const url = `http://localhost:8000/losing_trades/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setLosingTrades(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchWinRate(summaryRow) {

			const url = `http://localhost:8000/win_rate/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setWinRate(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchProfitFactor(summaryRow) {

			const url = `http://localhost:8000/profit_factor/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setProfitFactor(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchExpectancy(summaryRow) {

			const url = `http://localhost:8000/expectancy/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setExpectancy(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchAverageWin(summaryRow) {

			const url = `http://localhost:8000/average_win/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setAverageWin(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchAverageLoss(summaryRow) {

			const url = `http://localhost:8000/average_loss/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setAverageLoss(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchPayoffRatio(summaryRow) {

			const url = `http://localhost:8000/payoff_ratio/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setPayoffRatio(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchStartingCash(summaryRow) {

			const url = `http://localhost:8000/starting_cash/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setStartingCash(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchTotalCommission(summaryRow) {

			const url = `http://localhost:8000/total_commission/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setTotalCommission(result)

			} catch (error) {
					setError(error)

			} finally {
					setLoading(false)
			}

		};

		async function fetchTotalSlippageCost(summaryRow) {

			const url = `http://localhost:8000/total_slippage_cost/${summaryRow.id}`

			try{

				const response = await fetch(url);
				if(response.status >= 400){
					throw new Error(`Response status: ${response.status}`);
				}
				const result = await response.json();
				setTotalSlippageCost(result)

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

					<PerformanceStatistics finalEquity={finalEquity}
										   totalNetProfit={totalNetProfit}
										   returnPct={returnPct}
										   sharpeRatio={sharpeRatio}
										   annualizedPct={annualizedPct}
										   mdd={mdd}
										   calmarRatio={calmarRatio}
										   totalTrades={totalTrades}
										   winningTrades={winningTrades}
										   losingTrades={losingTrades}
										   winRate={winRate}
										   profitFactor={profitFactor}
										   expectancy={expectancy}
										   averageWin={averageWin}
										   averageLoss={averageLoss}
										   payoffRatio={payoffRatio}
										   startingCash={startingCash}
										   totalCommission={totalCommission}
										   totalSlippageCost={totalSlippageCost}
					/>

					<div className="results">
						<h1>Backtest results</h1>

						<Summary summaries={summaries}
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