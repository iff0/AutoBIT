Highcharts.chart('container', {
	chart: {
		plotBackgroundColor: null,
		plotBorderWidth: null,
		plotShadow: false,
		type: 'pie'
	},
	title: {
		text: '卷积层和全链接层参数量占比'
	},
	tooltip: {
		pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
	},
	plotOptions: {
		pie: {
			allowPointSelect: true,
			cursor: 'pointer',
			dataLabels: {
				enabled: false
			},
			showInLegend: true
		}
	},
	series: [{
		name: '参数量',
		colorByPoint: true,
		data: [{
			name: '卷积层',
			y: 95.61,
			sliced: true,
			selected: true
		}, {
			name: '全链接层',
			y: 4.39
		}]
	}]
});