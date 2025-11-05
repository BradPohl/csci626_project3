import json
from pathlib import Path
from collections import Counter
import argparse
import networkx as nx


def load_reports(path: str):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text)


def build_entity_graph(reports):
    """
    Build a graph with ONLY entity nodes:

      - Nodes: people + places
        * person:<name>  (type="person", label=<name>)
        * place:<name>   (type="place",  label=<name>)

      - Edges: two entities that co-occur in the SAME document
        Edge attribute:
          docs = [list of report IDs where they co-occur]
    """
    G = nx.Graph()

    for report in reports:
        doc_id = report.get("ID")
        persons = [p for p in report.get("PERSONS", []) if p]
        places = [pl for pl in report.get("PLACES", []) if pl]

        entity_ids = []

        # Person nodes
        for person in persons:
            pid = f"person:{person}"
            if not G.has_node(pid):
                G.add_node(pid, type="person", label=person)
            entity_ids.append(pid)

        # Place nodes
        for place in places:
            plid = f"place:{place}"
            if not G.has_node(plid):
                G.add_node(plid, type="place", label=place)
            entity_ids.append(plid)

        # For this document, connect every pair of entities
        for i in range(len(entity_ids)):
            for j in range(i + 1, len(entity_ids)):
                u, v = entity_ids[i], entity_ids[j]
                if G.has_edge(u, v):
                    docs = G[u][v].setdefault("docs", [])
                    if doc_id and doc_id not in docs:
                        docs.append(doc_id)
                else:
                    G.add_edge(u, v, docs=[doc_id] if doc_id else [])

    return G


def export_graph_for_d3(G, out_path: str):
    nodes = [{"id": n, **data} for n, data in G.nodes(data=True)]
    links = [
        {"source": u, "target": v, **data}
        for u, v, data in G.edges(data=True)
    ]
    graph_obj = {"nodes": nodes, "links": links}
    Path(out_path).write_text(json.dumps(graph_obj, indent=2), encoding="utf-8")


def compute_bar_data(reports, top_k: int = 20):
    person_counts = Counter(
        person
        for r in reports
        for person in r.get("PERSONS", [])
        if person
    )
    place_counts = Counter(
        place
        for r in reports
        for place in r.get("PLACES", [])
        if place
    )

    top_people = [
        {"name": name, "count": count}
        for name, count in person_counts.most_common(top_k)
    ]
    top_places = [
        {"name": name, "count": count}
        for name, count in place_counts.most_common(top_k)
    ]
    return {"people": top_people, "places": top_places}


def export_bars_for_d3(reports, out_path: str, top_k: int = 20):
    bar_data = compute_bar_data(reports, top_k=top_k)
    Path(out_path).write_text(json.dumps(bar_data, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Build entity graph.json and bars.json from reports.json"
    )
    parser.add_argument("input", help="Path to reports.json")
    parser.add_argument("--graph-out", default="graph1.json")
    parser.add_argument("--bars-out", default="bars1.json")
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()

    reports = load_reports(args.input)
    G = build_entity_graph(reports)
    export_graph_for_d3(G, args.graph_out)
    export_bars_for_d3(reports, args.bars_out, top_k=args.top_k)
    print(f"Wrote {args.graph_out} and {args.bars_out}")


if __name__ == "__main__":
    main()
