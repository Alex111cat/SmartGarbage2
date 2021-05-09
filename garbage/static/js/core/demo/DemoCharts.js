(function (namespace, $) {
	"use strict";

	var DemoCharts = function () {
		// Create reference to this instance
		var o = this;

		// Initialize app when document is ready
		$(document).ready(function () {
			o.initialize();

		});

	};
	var p = DemoCharts.prototype;


	// =========================================================================
	// MEMBERS
	// =========================================================================

	p.rickshawSeries = [[], []];
	p.rickshawGraph = null;
	p.rickshawRandomData = null;
	p.rickshawTimer = null;

	// =========================================================================
	// INIT
	// =========================================================================

	p.initialize = function () {
		// Rickshaw
		this._initRickshaw();
		this._initRickshawDemo2();
		
		// Sparkline
		this._initResponsiveSparkline();
		this._initInlineSparkline();

		// Knob
		this._initKnob();

		// Flot
		this._initFlotLine();
		this._initFlotRealtime();

		// Morris
		this._initMorris();
	};

	// =========================================================================
	// Rickshaw
	// =========================================================================

	p._initRickshaw = function () {
		// Don't init a rickshaw graph twice
		if (this.rickshawGraph !== null) {
			return;
		}

		var o = this;

		// Create random data
		this.rickshawRandomData = new Rickshaw.Fixtures.RandomData(50);
		for (var i = 0; i < 75; i++) {
			this.rickshawRandomData.addData(this.rickshawSeries);
		}

		// Init Richshaw graph
		this.rickshawGraph = new Rickshaw.Graph({
			element: $('#rickshawGraph').get(0),
			width: $('#rickshawGraph').closest('.card-body').width(),
			height: $('#rickshawGraph').height(),
			interpolation: 'linear',
			renderer: 'area',
			series: [
				{
					data: this.rickshawSeries[0],
					color: $('#rickshawGraph').data('color1'),
					name: 'temperature'
				}, {
					data: this.rickshawSeries[1],
					color: $('#rickshawGraph').data('color2'),
					name: 'heat index'
				}
			]
		});

		// Add hover info
		var hoverDetail = new Rickshaw.Graph.HoverDetail({
			graph: this.rickshawGraph
		});

		// Render graph
		this.rickshawGraph.render();

		// Add animated data
		clearInterval(this.rickshawTimer);
		this.rickshawTimer = setInterval(function () {
			o._refreshRickshaw();
		}, 2000);

		materialadmin.App.callOnResize(function () {
			o.rickshawGraph.configure({
				height: $('#rickshawGraph').height(),
				width: $('#rickshawGraph').closest('.card-body').width()
			});
			o.rickshawGraph.render();
		});
	};

	p._refreshRickshaw = function () {
		this.rickshawRandomData.removeData(this.rickshawSeries);
		this.rickshawRandomData.addData(this.rickshawSeries);
		this.rickshawGraph.update();
	};

	// =========================================================================
	// Rickshaw - demo 2
	// =========================================================================

	p._initRickshawDemo2 = function () {
		var seriesData = [[], [], [], [], []];
		var random = new Rickshaw.Fixtures.RandomData(50);
		for (var i = 0; i < 75; i++) {
			random.addData(seriesData);
		}
		var graph = new Rickshaw.Graph({
			element: $('#rickshawDemo2').get(0),
			renderer: 'multi',
			width: $('#rickshawDemo2').width(),
			height: 300,
			dotSize: 5,
			series: [
				{
					name: 'temperature',
					data: seriesData.shift(),
					color: 'rgba(255, 0, 0, 0.4)',
					renderer: 'stack'
				}, {
					name: 'heat index',
					data: seriesData.shift(),
					color: 'rgba(255, 127, 0, 0.4)',
					renderer: 'stack'
				}, {
					name: 'dewpoint',
					data: seriesData.shift(),
					color: 'rgba(127, 0, 0, 0.3)',
					renderer: 'scatterplot'
				}, {
					name: 'pop',
					data: seriesData.shift().map(function (d) {
						return {x: d.x, y: d.y / 4}
					}),
					color: 'rgba(0, 0, 127, 0.4)',
					renderer: 'bar'
				}, {
					name: 'humidity',
					data: seriesData.shift().map(function (d) {
						return {x: d.x, y: d.y * 1.5}
					}),
					renderer: 'line',
					color: 'rgba(0, 0, 127, 0.25)'
				}
			]
		});
		var slider = new Rickshaw.Graph.RangeSlider.Preview({
			graph: graph,
			element: document.querySelector('#slider')
		});
		graph.render();
		var detail = new Rickshaw.Graph.HoverDetail({
			graph: graph
		});
	};

	// =========================================================================
	// SPARKLINE
	// =========================================================================

	p._initResponsiveSparkline = function () {
		if ($('.sparkline3').length === 0) {
			return;
		}
		if ($('.sparkline4').length === 0) {
			return;
		}

		materialadmin.App.callOnResize(function () {
			var options = $('.sparkline3').data();
			options.type = 'line';
			options.width = '100%';
			options.height = '80px';
			$('.sparkline3').sparkline([3, 6, 5, 10, 8, 7, 9, 11, 12, 9, 14], options);
		});
		materialadmin.App.callOnResize(function () {
			var options = $('.sparkline4').data();
			options.type = 'line';
			options.width = '100%';
			options.height = '80px';
			$('.sparkline4').sparkline([14, 11, 13, 9, 11, 12, 10, 8, 7, 9, 3], options);
		});
	};

	p._initInlineSparkline = function () {
		if (!$.isFunction($.fn.sparkline)) {
			return;
		}

		$('.inlinesparkline').each(function () {
			var options = $(this).data();
			$(this).sparkline('html', options);
		});
	};

	// =========================================================================
	// KNOB
	// =========================================================================

	p._initKnob = function () {
		if (!$.isFunction($.fn.knob)) {
			return;
		}

		$('.dial').each(function () {
			var options = materialadmin.App.getKnobStyle($(this));
			$(this).knob(options);
		});
	};

	// =========================================================================
	// FLOT - line
	// =========================================================================

	p._initFlotLine = function () {
		var chart = $("#module");
 
		if (!$.isFunction($.fn.plot) || chart.length === 0) {
			return;
		}
                // var el = document.getElementById('module');
		var o = this;
		
		// alert(el.dataset.qid);
		var labelColor = chart.css('color');

		// alert(chart.data('qid'));
		var data = [
			{
				label: 'Pageviews',
				data: [
					
					[moment("2021-01-28").valueOf(), 5500],
					[moment("2021-01-29").valueOf(), 3500],
					[moment("2021-01-31").valueOf(), 4000],
					[moment("2021-01-31").valueOf(), 3450],
					[moment("2021-02-01").valueOf(), 3000]

				],
				last: true
			},
		
		];

		var options = {
			colors: chart.data('color').split(','),
			series: {
				shadowSize: 0,
				lines: {
					show: true,
					lineWidth: 2
				},
				points: {
					show: true,
					radius: 3,
					lineWidth: 2
				}
			},
			legend: {
				show: false
			},
			xaxis: {
				mode: "time",
				timeformat: "%d/%m/%y",
				color: 'rgba(0, 0, 0, 0)',
				font: {color: labelColor}
			},
			yaxis: {
				font: {color: labelColor}
			},
			grid: {
				borderWidth: 0,
				color: labelColor,
				hoverable: true
			}
		};

		chart.width('100%');
		var plot = $.plot(chart, data, options);

		var tip, previousPoint = null;
		chart.bind("plothover", function (event, pos, item) {
			if (item) {
				if (previousPoint !== item.dataIndex) {
					previousPoint = item.dataIndex;

					var x = item.datapoint[0];
					var y = item.datapoint[1];
					var tipLabel = '<strong>' + $(this).data('title') + '</strong>';
					var tipContent = y + " " + item.series.label.toLowerCase() + " on " + moment(x).format('dddd');

					if (tip !== undefined) {
						$(tip).popover('destroy');
					}
					tip = $('<div></div>').appendTo('body').css({left: item.pageX, top: item.pageY - 5, position: 'absolute'});
					tip.popover({html: true, title: tipLabel, content: tipContent, placement: 'top'}).popover('show');
				}
			}
			else {
				if (tip !== undefined) {
					$(tip).popover('destroy');
				}
				previousPoint = null;
			}
		});
	};

	// =========================================================================
	// FLOT - realtime
	// =========================================================================

	p._initFlotRealtime = function () {
		var chart = $("#realtime-chart");
		if (!$.isFunction($.fn.plot) || chart.length === 0) {
			return;
		}

		var o = this;
		var labelColor = chart.css('color');
		var options = {
			colors: chart.data('color').split(','),
			series: {
				shadowSize: 0,
				lines: {
					show: true,
					lineWidth: 1,
					fill: true
				}
			},
			legend: {
				show: false
			},
			xaxis: {
				show: false,
				font: {color: labelColor}
			},
			yaxis: {
				min: 0,
				max: 100,
				font: {color: labelColor}
			},
			grid: {
				borderWidth: 0,
				color: labelColor,
				hoverable: true
			}
		};

		// We use an inline data source in the example, usually data would
		// be fetched from a server
		var data = [];
		var totalPoints = 300;

		function getRandomData() {
			if (data.length > 0) {
				data = data.slice(1);
			}

			// Do a random walk
			while (data.length < totalPoints) {
				var prev = data.length > 0 ? data[data.length - 1] : 50;
				var y = prev + Math.random() * 10 - 5;

				if (y < 0) {
					y = 0;
				} else if (y > 100) {
					y = 100;
				}
				data.push(y);
			}

			// Zip the generated y values with the x values
			var res = [];
			for (var i = 0; i < data.length; ++i) {
				res.push([i, data[i]])
			}
			return res;
		}

		// Set up the control widget
		var updateInterval = 30;
		var plot = $.plot(chart, [getRandomData()], options);

		function update() {
			plot.setData([getRandomData()]);

			// Since the axes don't change, we don't need to call plot.setupGrid()
			plot.draw();
			setTimeout(update, updateInterval);
		}

		update();
	};


	// =========================================================================
	namespace.DemoCharts = new DemoCharts;
}(this.materialadmin, jQuery)); // pass in (namespace, jQuery):
