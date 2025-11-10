// Shared constants + app state

const BARS_URL = "bars1.json";
const GRAPH_URL = "graph1.json";

const graphState = {
  nodes: [],
  links: [],
  nodeElements: null,
  linkElements: null,
  adjacency: new Map(),
  width: 600,
  height: 600,
};

const selectedDocIds = new Set();

// which bars are selected?
const selectionState = {
  people: new Set(),
  places: new Set(),
};

// to re-style bars on selection changes
const chartState = {
  personBars: null,
  placeBars: null,
};

// helper to build adjacency map from links
function buildAdjacency(links) {
  const adj = new Map();
  links.forEach(l => {
    const s = typeof l.source === "object" ? l.source.id : l.source;
    const t = typeof l.target === "object" ? l.target.id : l.target;
    if (!adj.has(s)) adj.set(s, new Set());
    if (!adj.has(t)) adj.set(t, new Set());
    adj.get(s).add(t);
    adj.get(t).add(s);
  });
  return adj;
}