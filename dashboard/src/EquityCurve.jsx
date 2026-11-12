import { CartesianGrid, Area, AreaChart, XAxis, YAxis, Tooltip, Legend } from 'recharts';

// colours mirror the tokens in index.css (--border, --text-muted, --accent, --surface)
const BORDER = "#2a2f3a";
const MUTED = "#8b93a3";
const ACCENT = "#3b82f6";
const SURFACE = "#161a23";

function Equities( {equities} ) {

	const style={ width: '100%', aspectRatio: 5 }
	const tick={ fill: MUTED, fontSize: 12 }

	return(
			<>
				<div className="equity_chart">
					<h1>Equity Curve Chart</h1>

					<AreaChart style={style}
										 responsive={true}
										 data={equities}
										 margin={ { top: 8, right: 16, bottom: 24, left: 16 } }>

						<CartesianGrid stroke={BORDER} strokeDasharray="3 3" vertical={false}/>
						<Area dataKey="equity"
									type="monotone"
									strokeWidth={2}
									stroke={ACCENT}
									dot={false}
									name='Portfolio equity'/>
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
									 label={ { value: 'Equity ($)', position: 'insideLeft', angle: -90, fill: MUTED } }/>
						<Tooltip contentStyle={ { background: SURFACE, border: `1px solid ${BORDER}`, borderRadius: 6 } }
										 labelFormatter={ (day) => `Day ${day}` }
										 formatter={ (value) => value.toFixed(2) }/>
						{/* lifted out of the plot, up onto the title's row, just right of "Equity Curve Chart" */}
						<Legend position="insideTopLeft"
										iconType="plainline"
										wrapperStyle={ { top: -29, left: 185, width: "auto", fontSize: 13 } }/>

					</AreaChart>

				</div>
			</>
	)
}

export default Equities