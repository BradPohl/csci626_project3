// App initialization

Promise.all([
  d3.json(BARS_URL),
  d3.json(GRAPH_URL),
]).then(([barsData, graphData]) => {
  renderBarChart("#people-chart", barsData.people, "person");
  renderBarChart("#places-chart", barsData.places, "place");
  renderGraph(graphData);

  d3.select("#ask-btn").on("click", () => {
    const q = d3.select("#question").property("value");
    d3.select("#llm-output").text(
      "LLM call would go here.\n\nQuestion:\n" + q +
      "\n\n(Backend will use the selected document IDs from the right panel.)"
    );
  });
}).catch(err => {
  console.error("Error loading data:", err);
});