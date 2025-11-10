// Selection, highlighting, and doc list interactions

function toggleSelection(type, label) {
  const set = type === "person" ? selectionState.people : selectionState.places;
  if (set.has(label)) {
    set.delete(label);
  } else {
    set.add(label);
  }
  updateBarStyles();
  updateHighlights();
}

function updateBarStyles() {
  if (chartState.personBars) {
    chartState.personBars
      .classed("selected", d => selectionState.people.has(d.name));
  }
  if (chartState.placeBars) {
    chartState.placeBars
      .classed("selected", d => selectionState.places.has(d.name));
  }
}

function updateHighlights() {
  if (!graphState.nodeElements) return;

  const selectedIds = new Set();
  selectionState.people.forEach(name => selectedIds.add(`person:${name}`));
  selectionState.places.forEach(name => selectedIds.add(`place:${name}`));

  const adjacency = graphState.adjacency;

  // reset the selectedDocIds set before computing
  selectedDocIds.clear();

  // no selection → reset styles + clear docs
  if (selectedIds.size === 0) {
    graphState.nodeElements
      .attr("opacity", 0.9)
      .attr("stroke", "#111")
      .attr("stroke-width", 0.6)
      .attr("r", 5);

    graphState.linkElements
      .attr("stroke-opacity", 0.4)
      .attr("stroke-width", 1.0);

    updateDocList(new Set());
    return;
  }

  // neighbors: union of neighbors of all selected nodes
  const neighborIds = new Set(selectedIds);
  selectedIds.forEach(id => {
    const neigh = adjacency.get(id);
    if (neigh) {
      neigh.forEach(nid => neighborIds.add(nid));
    }
  });

  // style nodes
  graphState.nodeElements
    .attr("opacity", d => (neighborIds.has(d.id) ? 1 : 0.1))
    .attr("stroke", d => (selectedIds.has(d.id) ? "#fff" : "#111"))
    .attr("stroke-width", d => (selectedIds.has(d.id) ? 2 : 0.6))
    .attr("r", d => (selectedIds.has(d.id) ? 7 : 5));

  // style links + collect docs from active edges
  graphState.linkElements
    .attr("stroke-opacity", d => {
      const s = d.source.id ?? d.source;
      const t = d.target.id ?? d.target;
      const active = selectedIds.has(s) || selectedIds.has(t);
      if (active && Array.isArray(d.docs)) {
        d.docs.forEach(docId => selectedDocIds.add(docId));
      }
      return active ? 0.9 : 0.05;
    })
    .attr("stroke-width", d => {
      const s = d.source.id ?? d.source;
      const t = d.target.id ?? d.target;
      const active = selectedIds.has(s) || selectedIds.has(t);
      return active ? 2 : 0.5;
    });

  updateDocList(selectedDocIds);
}

function updateDocList(docIdSet) {
  const ul = d3.select("#doc-list");
  ul.selectAll("*").remove();

  const ids = Array.from(docIdSet);
  if (!ids.length) {
    ul.append("li").text("No documents selected.");
    return;
  }

  ul.selectAll("li")
    .data(ids)
    .enter()
    .append("li")
    .text(d => d)
    .on("click", (event, d) => {
      // clicking a doc removes it from current selection
      selectedDocIds.delete(d);
      updateDocList(selectedDocIds);
    });
}