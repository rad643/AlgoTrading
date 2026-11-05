import { useState } from "react"

function BacktestParameters( {clearSummaryRows, addRun} ){

    const [strategy, setStrategy] = useState("Trend")
		const [asset,setAsset] = useState("")
		const [cash,setCash] = useState(0)
		const [timeframe,setTimeframe] = useState("15Min")
		const [start,setStart] = useState("")
		const [end,setEnd] = useState("")
		const [limit,setLimit] = useState(0)
		const [fixedBPS, setFixedBPS] = useState(0.0005)
		const [flatFeePerShare, setFlatFeePerShare] = useState(0.005)
		const [positionSizing, setPositionSizing] = useState(0.2)

    return(
        <>

        <div className="params-panel">
        	<h2>Backtest Parameters</h2>
          <Strategy strategy={strategy}
                    setStrategy={setStrategy}
					/>
					<Ticker asset={asset}
									setAsset={setAsset}
					/>
					<Cash cash={cash}
								setCash={setCash}
					/>
					<Timeframe timeframe={timeframe}
										 setTimeframe={setTimeframe}
					/>
					<Start start={start}
								 setStart={setStart}
					/>
					<End end={end}
					     setEnd={setEnd}
					/>
					<Limit limit={limit}
					     setLimit={setLimit}
					/>
					<Slippage fixedBPS={fixedBPS}
									  setFixedBPS={setFixedBPS}
					/>
					<Comission flatFeePerShare={flatFeePerShare}
									  setFlatFeePerShare={setFlatFeePerShare}
					/>
					<PositionSize positionSizing={positionSizing}
											  setPositionSizing={setPositionSizing}
					/>
					<Button clearSummaryRows={clearSummaryRows}
									addRun={addRun}
									strategy={strategy}
									asset={asset}
									cash={cash}
									timeframe={timeframe}
									start={start}
									end={end}
									limit={limit}
									fixedBPS={fixedBPS}
									flatFeePerShare={flatFeePerShare}
									positionSizing={positionSizing}
					/>
        </div>

        </>
    )
}



function Strategy( {strategy, setStrategy} ){

	return(
		<>

		<label>
			Strategy

			<select
				value={strategy}
				onChange={ (event) => setStrategy(event.target.value) } >
				<option value="Trend">Trend</option>
  			<option value="Mean Reversion">Mean Reversion</option>
			</select>
			
		</label>

		</>
	)
}



function Ticker( {asset,setAsset} ){
	return(
		<>

		<label>
			Asset/Ticker

			<input type="text"
						placeholder="Choose a ticker"
						value={asset}
						onChange={ (event) => setAsset(event.target.value) }
			/>

		</label>

		</>
	)
}



function Cash( {cash,setCash} ){

	return(
		<>
		
		<label data-prefix="$">
		Initial Cash

			<input type="number"
							placeholder="Choose a starting cash value"
							value={cash}
							onChange={ (event) => setCash(event.target.value) }
			/>

		</label>
		
		</>
	)

}



function Timeframe( {timeframe,setTimeframe} ){

	return(
		<>
		
		<label>
		Timeframe

			<select
				value={timeframe}
				onChange={ (event) => setTimeframe(event.target.value) } >
				<option value="15Min">15Min</option>
  			<option value="1Hour">1Hour</option>
				<option value="1Day">1Day</option>
				<option value="1Week">1Week</option>
				<option value="1Month">1Month</option>
			</select>

		</label>
		
		</>
	)

}



function Start( {start,setStart} ){

	return(
		<>
		
		<label>
		Start date

			<input type="date"
							placeholder="Choose the start date"
							value={start}
							onChange={ (event) => setStart(event.target.value) }
			/>

		</label>
		
		</>
	)

}



function End( {end,setEnd} ){

	return(
		<>
		
		<label>
		End date

			<input type="date"
							placeholder="Choose the end date"
							value={end}
							onChange={ (event) => setEnd(event.target.value) }
			/>

		</label>
		
		</>
	)

}



function Limit( {limit,setLimit} ){

	return(
		<>
		
		<label>
		Limit 

			<input type="number"
							placeholder="Choose how many bars can fit into 1 page"
							value={limit}
							onChange={ (event) => setLimit(event.target.value) }
			/>

		</label>
		
		</>
	)

}



function Slippage( {fixedBPS,setFixedBPS} ){

	return(
		<>
		
		<label data-unit="of price">
		Slippage

			<input type="number"
							placeholder="Choose a slippage value"
							value={fixedBPS}
							onChange={ (event) => setFixedBPS(event.target.value) }
			/>

		</label>
		
		</>
	)

}



function Comission( {flatFeePerShare,setFlatFeePerShare} ){

	return(
		<>
		
		<label data-unit="$/share">
		Comission

			<input type="number"
							placeholder="Choose a comission value"
							value={flatFeePerShare}
							onChange={ (event) => setFlatFeePerShare(event.target.value) }
			/>

		</label>
		
		</>
	)

}


function PositionSize( {positionSizing, setPositionSizing} ){

	return(
		<>
		
		<label data-unit="of cash">
		Position Size 

			<select
				value={positionSizing}
				onChange={ (event) => setPositionSizing(event.target.value) } >
				<option value="0.05">5%</option>
  			<option value="0.1">10%</option>
				<option value="0.2">20%</option>
				<option value="0.25">25%</option>
				<option value="0.5">50%</option>
				<option value="1">100%</option>
			</select>

		</label>
		
		</>
	)

}



function Button( {clearSummaryRows, addRun , strategy, asset, cash, timeframe, start , end, limit, fixedBPS, flatFeePerShare, positionSizing} ) {

	async function onButtonClick() {

		const url= "http://localhost:8000/run_backtest"

		try {

			const response = await fetch(url , {
				method: "POST" , 
				body: JSON.stringify( {"trendMethod": strategy==="Trend",
															"symbol": asset,
															"cashValue": cash,
															"ticker_name": asset,
															"timeframe": timeframe,
															"start": start,
															"end": end,
															"limit": limit,
															"fixed_bps": fixedBPS,
														  "flat_fee_per_share": flatFeePerShare,
															"positionSizing": positionSizing} ) ,
					headers : { "Content-Type": "application/json", }
			});
			if(!response.ok){	
				throw new Error(`Response status: ${response.status}`);
			}
			const result = await response.json()
			const summaryRow = result["summary"]
			addRun(summaryRow)

		} catch(error) {

			console.log(`Error: ${error}`)

		}

	}

  return (
		<div>

			<button
				type="submit"
				onClick={ () => onButtonClick() }
				disabled={!asset || !cash || !start || !end || !limit || !fixedBPS || !flatFeePerShare || !positionSizing}
			>
				▶ Run backtest
			</button>

			<button 
			type="submit"
			onClick={ () => clearSummaryRows() }
			>
				Delete Summary rows
			</button>

		</div>
  );
}


export default BacktestParameters