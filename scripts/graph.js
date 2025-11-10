// Graph rendering (nodes = people/places, links = co-occur)

function renderGraph(graphData) {
  const svg = d3.select("#graph-svg");
  const width = svg.node().clientWidth || 600;
  const height = svg.node().clientHeight || 600;

  graphState.width = width;
  graphState.height = height;

  svg.attr("viewBox", [0, 0, width, height]);
  svg.selectAll("*").remove();

  const container = svg.append("g").attr("class", "graph-container");

  // background rect so you can pan by dragging empty space
  container.append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", width)
    .attr("height", height)
    .attr("fill", "transparent");

  const nodes = graphData.nodes.map(d => ({ ...d }));
  const links = graphData.links.map(d => ({ ...d }));

  graphState.nodes = nodes;
  graphState.links = links;
  graphState.adjacency = buildAdjacency(links);

  const link = container.append("g")
    .attr("stroke", "#555")
    .attr("stroke-opacity", 0.4)
    .selectAll("line")
    .data(links)
    .join("line")
    .attr("stroke-width", 1.0);

  const color = d => {
    if (d.type === "person") return "#22c55e";
    if (d.type === "place")  return "#38bdf8";
    return "#a855f7";
  };

  const node = container.append("g")
    .attr("stroke", "#111")
    .attr("stroke-width", 0.6)
    .selectAll("circle")
    .data(nodes)
    .join("circle")
    .attr("r", 5)
    .attr("fill", color)
    .attr("class", "graph-node")
    .call(
      d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    )
    .on("click", (event, d) => {
      // clicking nodes toggles selection (relies on interactions.js)
      toggleSelection(d.type, d.label);
    });

  node.append("title").text(d => d.label || d.id);

  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(60))
    .force("charge", d3.forceManyBody().strength(-120))
    .force("center", d3.forceCenter(width / 2, height / 2));

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
  });

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }

  // zoom & pan
  const zoom = d3.zoom()
    .scaleExtent([0.2, 5])
    .on("zoom", (event) => {
      container.attr("transform", event.transform);
    });

  svg.call(zoom).call(zoom.transform, d3.zoomIdentity);

  graphState.nodeElements = node;
  graphState.linkElements = link;
}