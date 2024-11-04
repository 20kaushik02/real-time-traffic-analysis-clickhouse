import { useEffect, useState } from 'react'
import Chart from 'react-apexcharts'

const LineChart = ({ name, data, xaxis, ytitle }) => {
	const [chartData, setChartData] = useState([{
		name,
		data
	}])
	const [chartOptions, setChartOptions] = useState({
		chart: {
			type: 'line',
			height: 350,
			width: 540,
		},
		stroke: {
			width: 1
		},
		xaxis,
		yaxis: {
			title: {
				text: ytitle,
			},
		},
	})

	return <Chart
		options={chartOptions}
		series={chartData}
		type={chartOptions.chart.type}
		height={chartOptions.chart.height}
	/>

}

export default LineChart
