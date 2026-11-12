import { CartesianGrid, Area, AreaChart, XAxis, YAxis, Tooltip, Legend } from 'recharts';

// colours mirror the tokens in index.css (--border, --text-muted, --loss, --surface)
const BORDER = "#2a2f3a";
const MUTED = "#8b93a3";
const ACCENT = "#ef4444";
const SURFACE = "#161a23";

function Drawdowns( {drawdowns} ) {

	const style={ width: '100%', aspectRatio: 5 }
	const tick={ fill: MUTED, fontSize: 12 }

	return(
			<>
				<div className="drawdown_series_chart">
					<h1>Drawdown Series Chart</h1>

					<AreaChart style={style}
										 responsive={true}
										 data={drawdowns}
										 margin={ { top: 8, right: 16, bottom: 24, left: 16 } }>

						<CartesianGrid stroke={BORDER} strokeDasharray="3 3" vertical={false}/>
						<Area dataKey="drawdown_pct"
									type="monotone"
									strokeWidth={2}
									stroke={ACCENT}
									fill={ACCENT}
									fillOpacity={0.35}
									dot={false}
									name='Drawdown'/>
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
									 tickFormatter={ (v) => `${v.toFixed(1)}%` }
									 label={ { value: 'Drawdown (%)', position: 'insideLeft', angle: -90, fill: MUTED } }/>
						<Tooltip contentStyle={ { background: SURFACE, border: `1px solid ${BORDER}`, borderRadius: 6 } }
										 labelFormatter={ (day) => `Day ${day}` }
										 formatter={ (value) => value.toFixed(2) }/>
						{/* lifted out of the plot, up onto the title's row, just right of "Drawdown Series Chart" */}
						<Legend position="insideTopLeft"
										iconType="plainline"
										wrapperStyle={ { top: -29, left: 215, width: "auto", fontSize: 13 } }/>

					</AreaChart>

				</div>
			</>
	)
}

export default Drawdowns