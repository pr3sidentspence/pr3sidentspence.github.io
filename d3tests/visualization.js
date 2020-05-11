var svg = d3.select("#map")
    .append("svg")
    .attr("height", 200) //height + margin.top + margin.bottom)
    .attr("width", 500) //width + margin.left + margin.right)
    .append("g");

var files = ["world.topojson"];

Promise.all(files.map(url => d3.json(url))).then(function (values) {
    console.log(values)
});
