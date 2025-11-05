# Entity Knowledge Graph Explorer

This project turns a collection of semi-structured intelligence-style reports into:

1. **Structured JSON**  
2. A **knowledge graph** of people and places (as entities)  
3. **Bar charts** of the most frequent people/places  
4. An interactive **D3.js interface** where:
   - Bars represent top people/places
   - Nodes represent people/places
   - Edges represent co-occurrence in documents (with doc IDs on each edge)
   - Clicking bars filters/highlights the graph and shows the related documents

---

## Pipeline Overview

**Input → Output**

1. `dataset.txt`  
   Raw text file of reports in blocks starting with `REPORT`, with fields like `ID`, `REPORTDATE`, `PERSONS`, `PLACES`, etc.

2. `parse_reports.py`  
   Parses `dataset.txt` into a list of JSON objects (one per report).

3. `build_graph_and_bars.py`  
   Takes `reports.json` and builds:
   - `graph.json` – entity co-occurrence graph (for D3 force layout)
   - `bars.json` – top-people and top-places counts (for D3 bar charts)

4. `index.html`  
   Loads `graph.json` and `bars.json` with D3 and renders:
   - Two bar charts (people + places)
   - A force-directed graph of people/places
   - A side panel with a document list and an LLM question stub

---

## Data Model

### Parsed Reports (`reports.json`)

Each report is a JSON object like:

```json
{
  "ID": "FBI_1",
  "REPORTDATE": "4/28/2003",
  "REFERENCEID": "CIA_7",
  "REPORTSOURCE": "Canadian Security Intelligence Service",
  "REPORTDESCRIPTION": "This report concerns ...",
  "PERSONS": [
    "Abdillah Zinedine",
    "Abu Hafs"
  ],
  "DATES": [
    "4/2/2003",
    "4/1/2003"
  ],
  "PLACES": [
    "/Paris/ /France",
    "Walden Ave./Buffalo/New York/USA"
  ],
  "ORGANIZATIONS": [
    "Surete' de l'Etat"
  ]
}
