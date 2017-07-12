<!DOCTYPE html>
<meta charset="utf-8">
<style> /* set the CSS */

 .line {
     fill: none;
     stroke: steelblue;
     stroke-width: 2px;
 }

</style>
<body>

    <!-- load the d3.js library -->     
    <script src="https://d3js.org/d3.v4.min.js"></script>
    <script>

     // set the dimensions and margins of the graph
     var margin = {top: 20, right: 20, bottom: 30, left: 50},
	 width = 800 - margin.left - margin.right,
	 height = 600 - margin.top - margin.bottom;

     // set the ranges
     var x = d3.scaleLinear().range([0, width]);
     var y = d3.scaleLinear().range([height, 0]);

     // define the line
     var line = d3.line()
		  .x(function(d) { return x(d[0]); })
		  .y(function(d) { return y(d[1]); });

     // Define the axes
     var xAxis = d3.axisBottom(x).ticks(5);
     var yAxis = d3.axisLeft(y).ticks(5);

     // append the svg obgect to the body of the page
     // appends a 'group' element to 'svg'
     // moves the 'group' element to the top left margin
     var svg = d3.select("body").append("svg")
		 .attr("width", width + margin.left + margin.right)
		 .attr("height", height + margin.top + margin.bottom)
		 .append("g")
		 .attr("transform",
		       "translate(" + margin.left + "," + margin.top + ")");
     
     // Get the data
     var data = [];
     d3.json("http://127.0.0.1:5000/get/sink/logger?keys=\"log\"",
	     function(error, obj) {
		 if (error) throw error;
		 
		 // grab data
		 data.push(obj.log.object);
		 // console.log(obj);
		 // console.log(data);

		 // Scale the range of the data
		 x.domain(d3.extent(data, function(d) { return d[0]; }));
		 y.domain(d3.extent(data, function(d) { return d[1]; }));
		 
		 // Add the line path.
		 svg.append("path")
		    .data([data])
		    .attr("class", "line")
		    .attr("d", line);
		 
		 // Add the x-axis.
                 svg.append("g")
		    .attr("transform", "translate(0," + height + ")")
		    .call(xAxis);
		 
		 // Add the Y Axis
		 svg.append("g")
		    .call(yAxis);
		 
	     });

     console.log(data);
     
     // Update the data on a timer
     var inter = setInterval(function() {
         updateData();
     }, 5000); 
     
     // Update data section
     function updateData() {
	 
	 // Get the data again
	 d3.json("http://127.0.0.1:5000/get/sink/logger?keys=\"log\"",
		 function(error, obj) {
		     if (error) throw error;

		     // grab data
		     var data = obj.log.object;
		     // console.log(obj);
		     // console.log(data);

		     // Scale the range of the data again
		     x.domain(d3.extent(data, function(d) { return d[0]; }));
		     y.domain(d3.extent(data, function(d) { return d[1]; }));
		     
		     // Select the section we want to apply our changes to
		     var svg = d3.select("body").transition();
		     
		     // Make the changes
		     svg.select(".line")   // change the line
			.duration(750)
			.attr("d", line(data));
		     svg.select(".x.axis") // change the x axis
			.duration(750)
			.call(xAxis);
		     svg.select(".y.axis") // change the y axis
			.duration(750)
			.call(yAxis);
		     
		 });
	 
     }
     
    </script>
</body>
