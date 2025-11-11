// App initialization + LLM ask handler (replaces stub)

Promise.all([
  d3.json(BARS_URL),
  d3.json(GRAPH_URL),
]).then(([barsData, graphData]) => {
  renderBarChart("#people-chart", barsData.people, "person");
  renderBarChart("#places-chart", barsData.places, "place");
  renderGraph(graphData);

  d3.select("#ask-btn").on("click", async () => {
    const q = d3.select("#question").property("value") || '';
    d3.select("#llm-output").text('Loading...');

    try {
      const resp = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: q,
          docIds: Array.from(selectedDocIds) // uses the shared Set
        })
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: 'unknown' }));
        d3.select("#llm-output").text('Error: ' + (err.error || JSON.stringify(err)));
        return;
      }

      const data = await resp.json();
      d3.select("#llm-output").text(data.answer || JSON.stringify(data));
    } catch (err) {
      d3.select("#llm-output").text('Request failed: ' + (err.message || err));
    }
  });
}).catch(err => {
  console.error("Error loading data:", err);
});