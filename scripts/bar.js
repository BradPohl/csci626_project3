// Bar chart rendering

function renderBarChart(svgId, data, type) {
  const svg = d3.select(svgId);
  const margin = { top: 10, right: 10, bottom: 20, left: 80 };
  const width = (svg.node().clientWidth || 260) - margin.left - margin.right;
  const height = (svg.node().clientHeight || 220) - margin.top - margin.bottom;

  svg.attr("viewBox", [0, 0, width + margin.left + margin.right, height + margin.top + margin.bottom]);
  svg.selectAll("*").remove();

  const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

  const y = d3.scaleBand()
    .domain(data.map(d => d.name))
    .range([0, height])
    .padding(0.15);

  const x = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.count) || 1])
    .nice()
    .range([0, width]);

  const bars = g.selectAll(".bar")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", 0)
    .attr("y", d => y(d.name))
    .attr("height", y.bandwidth())
    .attr("width", d => x(d.count))
    .attr("fill", type === "person" ? "#22c55e" : "#38bdf8")
    .on("click", (event, d) => {
      toggleSelection(type, d.name);
    });

  // store bar selections for styling later
  if (type === "person") {
    chartState.personBars = bars;
  } else {
    chartState.placeBars = bars;
  }

  g.selectAll(".bar-label")
    .data(data)
    .enter()
    .append("text")
    .attr("x", d => x(d.count) + 3)
    .attr("y", d => y(d.name) + y.bandwidth() / 2 + 3)
    .attr("fill", "#ddd")
    .attr("font-size", 7)
    .text(d => d.count);

  const yAxis = d3.axisLeft(y).tickSize(0);
  const xAxis = d3.axisBottom(x).ticks(4).tickFormat(d3.format("d"));

  g.append("g")
    .attr("class", "axis y-axis")
    .call(yAxis)
    .selectAll("text")
    .style("font-size", "8px");

  g.append("g")
    .attr("class", "axis x-axis")
    .attr("transform", `translate(0,${height})`)
    .call(xAxis);
}