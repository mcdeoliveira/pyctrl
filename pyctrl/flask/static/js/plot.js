//   * points = [
//   *     {
//     id: 'New York',
//     values: [
//     {date: 0, value: 0},
//     {date: 1000, value: 1},
//     {date: 2000, value: -1},
//     {date: 3000, value: 0},
//     ]
//   *     },
//   *     {
//     id: 'Austin',
//     values: [
//     {date: 0, value: -1},
//     {date: 1000, value: 1},
//     {date: 2000, value: 3},
//     {date: 3000, value: 2},
//     ]
//   *     },
//   *     {
//     id: 'San Francisco',
//     values: [
//     {date: 0, value: 1},
//     {date: 1000, value: 2},
//     {date: 2000, value: 3},
//     {date: 3000, value: 3},
//     ]
//   *     },
//   * ];

function key(d) { return d.id; };

function create_plot(plot, time, points, interval) {

    if (time.length == 0) {
	
	// no data available yet
	console.log("No data available. Will try again...");
	setTimeout(function() { get_data(create_plot, interval); }, interval);
	return;
	
    }
    
    var svg = d3.select("svg");

    // create plot object
    for (var x in plot) if (plot.hasOwnProperty(x)) delete plot[x];
    
    // margin, witdth and height
    plot.margin = {top: 20, right: 80, bottom: 30, left: 50};
    plot.width = svg.attr("width") - plot.margin.left - plot.margin.right;
    plot.height = svg.attr("height") - plot.margin.top - plot.margin.bottom;

    plot.duration = 30;

    // create group for lines
    var g = svg.append("g")
	.attr("transform",
	      "translate(" + plot.margin.left + "," + plot.margin.top + ")");
    
    g.append("defs").append("clipPath")
        .attr("id", "clip")
        .append("rect")
        .attr("width", plot.width)
        .attr("height", plot.height + plot.margin.bottom);
    
    // x, y and z
    plot.x = d3.scaleLinear().range([0, plot.width]);
    plot.y = d3.scaleLinear().range([plot.height, 0]),
    plot.z = d3.scaleOrdinal(d3.schemeCategory10);
    
    // line
    plot.line = d3.line()
	.curve(d3.curveLinear)
	.x(function(d) { return plot.x(d.date); })
	.y(function(d) { return plot.y(d.value); });

    // copy time and points
    plot.time = time.slice();
    plot.points = points.slice();

    // calculate domains
    var domain = d3.extent(plot.time);
    // console.log(domain);
    domain[0] = Math.min(domain[0], domain[1] - plot.duration);
    domain[1] = domain[0] + plot.duration;
    plot.x.domain(domain);

    plot.y.domain([
	d3.min(plot.points,
	       function(c) {
		   return d3.min(c.values,
				 function(d) { return d.value; });
	       }),
	d3.max(plot.points,
	       function(c) {
		   return d3.max(c.values,
				 function(d) { return d.value; });
	       })
    ]);
    
    plot.z.domain(points.map(function(c) { return c.id; }));

    // create sub group for x-axis
    plot.xAxis = d3.axisBottom(plot.x)
	.ticks(10);

    plot.yAxis = d3.axisLeft(plot.y)
	.ticks(10);
    
    // create sub group for y-axis
    g.append("g")
	.attr("class", "axis axis--y")
	.call(plot.yAxis);

    // group for x-axis and lines
    g = g.append("g")
	.attr("class", "frame")
	.attr("clip-path", "url(#clip)");
    
    // create lines
    // g = plot.plot.append("g")
    // 	.attr("class", "plot_line_container")
    // 	.attr("clip-path", "url(#clip)")
    
    plot.plot = g.append("g")
    	.attr("class", "plot_line_container")
    
    // create sub group for x-axis
    plot.plot.append("g")
	.attr("class", "axis axis--x")
	.attr("transform", "translate(0," + plot.height + ")")
	.call(plot.xAxis);
    
    g = plot.plot.selectAll(".plot_line")
    	.data(plot.points, key)
    
    plot.lines = g.enter()
    	.append("path")
    	.attr("class", "plot_line")
    	.attr("d", function(d) { return plot.line(d.values); })
    	.style("stroke", function(d) { return plot.z(d.id); });

    // console.log(plot);
    
    // then update every 10 seconds
    console.log("Getting data loop started...");
    setInterval(function() { get_data(update_plot, interval); }, interval);
    
};

function update_plot(plot, time, points, interval) {
    
    // console.log("update_plot");
    
    var bulk = true;
    if (bulk) {
	
	do_update_plot(plot, time, points, interval);
	
    } else {

	var dx = time[time.length-1] - plot.time[plot.time.length-1];

	var n = time.length;
	for (var i = 0; i < n; i++) {
	    var point = _.map(plot.points,
			      function(obj) {
				  var d = _.find(points,
						 function(e) { return e.id == obj.id; } );
				  return {
				      id: obj.id,
				      values: [d.values[i]]
				  };
			      });
	    
	    //console.log(point);
	    
	    do_update_plot(plot, [time[i]], point, dx/n);
	};
    }
    
};


function do_update_plot(plot, time, points, interval) {

    // console.log("do_update_plot");

    var dx = time[time.length-1] - plot.time[plot.time.length-1];
    // console.log("dx = " + dx);
    
    if (Number.isNaN(dx) || dx == 0) {
	// console.log("WILL RETURN");
	return;
    }
    
    // add to lines
    var n = time.length;
    _.map(plot.points, function(obj) {
	var d = _.find(points,
		       function(e) { return e.id == obj.id; } );
	for (i = 0; i < n; i++) {
	    obj.values.push(d.values[i]);
	}
    });
    
    // add to time
    for (i = 0; i < n; i++) {
	plot.time.push(time[i]);
    }

    // recalculate domains
    var domain = d3.extent(plot.time);
    if (domain[1] - domain[0] > plot.duration) {
	domain[0] = domain[1] - plot.duration;
    } else {
	domain[0] = domain[1] - plot.duration;
    }
    domain[1] = domain[0] + plot.duration;
    plot.x.domain(domain);
    
    plot.y.domain([
	d3.min(plot.points,
	       function(c) {
		   return d3.min(c.values,
				 function(d) { return d.value; });
	       }),
	d3.max(plot.points,
	       function(c) {
		   return d3.max(c.values,
				 function(d) { return d.value; });
	       })
    ]);

    // console.log(plot.points);
    
    // Select the section we want to apply our changes to
    var svg = d3.select("svg");

    // Make the changes
    plot.lines
	.data(plot.points)
	.attr("d", function(d) { return plot.line(d.values); });
    
    svg.select(".axis--x") // change the x axis
        .call(plot.xAxis);
    
    svg.select(".axis--y") // change the y axis
        .call(plot.yAxis);
    
    plot.plot
	.attr("transform", "translate(" + plot.x(domain[0] + dx) + ")")
	.transition()
	.duration(0.95*interval)
	.ease(d3.easeLinear)
	.attr("transform", "translate(" + plot.x(domain[0]) + ")");
    
    // remove old values
    var ind = plot.time.findIndex(function(d) { return d >= domain[0]; } );
    //console.log(ind);
    if (ind > 0) {
    	//console.log('REMOVING');
    	plot.time.splice(0, ind - 1);
    	_.map(plot.points, function(obj) {
    	    obj.values.splice(0, ind - 1);
    	});
    	//console.log(plot.time);
    	//console.log(plot.points);
    }
    
};
