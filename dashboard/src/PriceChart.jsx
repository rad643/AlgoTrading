import { CartesianGrid, Line, LineChart, ReferenceDot, XAxis, YAxis, Tooltip, Legend } from 'recharts';

// colours mirror the tokens in index.css (--border, --text-muted, --accent, --profit, --loss, --surface)
const BORDER = "#2a2f3a";
const MUTED = "#8b93a3";
const ACCENT = "#3b82f6";
const AVERAGE = "#f59e0b";
const PROFIT = "#22c55e";
const LOSS = "#ef4444";
const SURFACE = "#161a23";

// marker shapes: ▲ for a buy, ▼ for a sell, centred on the point
function BuyMarker( {cx, cy} ) {
	return <path d={`M ${cx} ${cy - 6} L ${cx + 6} ${cy + 5} L ${cx - 6} ${cy + 5} Z`} fill={PROFIT} />
}

function SellMarker( {cx, cy} ) {
	return <path d={`M ${cx} ${cy + 6} L ${cx + 6} ${cy - 5} L ${cx - 6} ${cy - 5} Z`} fill={LOSS} />
}

function Prices( {prices, trades} ) {

	const style={ width: '100%', aspectRatio: 3.5 }
	const tick={ fill: MUTED, fontSize: 12 }

	return(
			<>
				<div className="price_chart">
					<h1>Price Chart</h1>

					<LineChart style={style}
										 responsive={true}
										 data={prices}
										 margin={ { top: 8, right: 16, bottom: 24, left: 16 } }>

						<CartesianGrid stroke={BORDER} strokeDasharray="3 3" vertical={false}/>
						<Line dataKey="closing_price"
									type="monotone"
									strokeWidth={2}
									stroke={ACCENT}
									dot={false}
									name='Close'/>
						<Line dataKey="average"
									type="monotone"
									strokeWidth={2}
									stroke={AVERAGE}
									dot={false}
									name='Running average'/>
						{/* legend-only entries for the markers: these keys exist on no row, so nothing is drawn */}
						<Line dataKey="buy_signal" stroke={PROFIT} legendType="triangle" name='Buy' />
						<Line dataKey="sell_signal" stroke={LOSS} legendType="triangle" name='Sell' />
						<XAxis dataKey="day"
									 tick={tick}
									 stroke={BORDER}
									 minTickGap={24}
									 label={ { value: "Trading day", position: "insideBottom", offset: -16, fill: MUTED } }/>
						<YAxis
									 domain={ ['dataMin', 'dataMax'] }
									 width={72}
									 tick={tick}
									 stroke={BORDER}
									 tickFormatter={ (v) => Math.round(v).toLocaleString() }
									 label={ { value: 'Price ($)', position: 'insideLeft', angle: -90, fill: MUTED } }/>
						<Tooltip contentStyle={ { background: SURFACE, border: `1px solid ${BORDER}`, borderRadius: 6 } }
										 labelFormatter={ (day) => `Day ${day}` }
										 formatter={ (value) => value.toFixed(2) }/>
						{/* one ▲ per trade entry and one ▼ per trade exit, at the executed price */}
						{
							trades.map( (trade) => (
								<ReferenceDot key={`buy-${trade.id}`}
															x={trade.entry_day}
															y={trade.entry_price}
															ifOverflow="extendDomain"
															shape={BuyMarker}/>
							))
						}
						{
							trades.map( (trade) => (
								<ReferenceDot key={`sell-${trade.id}`}
															x={trade.exit_day}
															y={trade.exit_price}
															ifOverflow="extendDomain"
															shape={SellMarker}/>
							))
						}
						{/* lifted out of the plot, up onto the title's row, just right of "Price Chart" */}
						<Legend position="insideTopLeft"
										iconSize={10}
										wrapperStyle={ { top: -29, left: 120, width: "auto", fontSize: 13 } }/>

					</LineChart>

				</div>
			</>
	)
}

export default Prices
