"""BSD3513 Lab Report 1 - directed graph BFS/DFS explorer.

Run the app:
    streamlit run SD24057_Lab1.py

Test the traversal algorithms without installing Streamlit:
    python SD24057_Lab1.py --self-test

The official A-H edge directions are transcribed from the figure on page 2 of
'LabReport_BSD3513_#1(1).pdf'. The exercise does not specify a start node;
A is explicitly chosen as the default for reproducible comparisons.
"""

from __future__ import annotations

import json
import sys
from collections import deque
from typing import Any


# Keep outgoing neighbours in alphabetical order when running either search.
# The source is the ORIGINAL directed A-H graph in the lab report, not UCS_img1.
LAB_GRAPH: dict[str, list[str]] = {
    "A": ["B", "D"],
    "B": ["C", "E", "G"],
    "C": ["A"],
    "D": ["C"],
    "E": ["H"],
    "F": [],
    "G": ["F"],
    "H": ["F", "G"],
}


def normalize_graph(raw: Any) -> dict[str, list[str]]:
    """Validate a JSON-like adjacency list and normalize every node/edge.

    Edges remain DIRECTED. Unknown target nodes are added as sinks.
    Duplicate neighbours are removed. Node names are case-sensitive.
    """
    if not isinstance(raw, dict) or not raw:
        raise ValueError("Graph must be a nonempty JSON object of node: [neighbours].")
    if len(raw) > 50:
        raise ValueError("At most 50 source nodes are permitted.")

    graph: dict[str, list[str]] = {}
    for original_node, original_neighbours in raw.items():
        if not isinstance(original_node, str) or not original_node.strip():
            raise ValueError("Each node name must be a nonempty string.")
        node = original_node.strip()
        if node in graph:
            raise ValueError(f"Duplicate node name after stripping whitespace: {node}")
        if not isinstance(original_neighbours, list):
            raise ValueError(f"Neighbours of {node} must be provided in a JSON list.")
        for neighbour in original_neighbours:
            if not isinstance(neighbour, str) or not neighbour.strip():
                raise ValueError(f"Every neighbour of {node} must be a nonempty string.")
        graph[node] = sorted({n.strip() for n in original_neighbours}, key=lambda s: (s.casefold(), s))

    targets = {neighbour for neighbours in graph.values() for neighbour in neighbours}
    for neighbour in targets:
        graph.setdefault(neighbour, [])
    if len(graph) > 50:
        raise ValueError("At most 50 total nodes are permitted.")
    return {node: graph[node] for node in sorted(graph, key=lambda s: (s.casefold(), s))}


def _check_search_inputs(graph: dict[str, list[str]], start: str, goal: str | None) -> None:
    if start not in graph:
        raise ValueError(f"Starting node {start!r} does not exist in the graph.")
    if goal is not None and goal not in graph:
        raise ValueError(f"Goal node {goal!r} does not exist in the graph.")


def build_path(parents: dict[str, str | None], target: str | None) -> list[str]:
    """Reconstruct a search-tree path; empty if not reached or unspecified."""
    if target is None or target not in parents:
        return []
    path: list[str] = []
    cursor: str | None = target
    while cursor is not None:
        path.append(cursor)
        cursor = parents[cursor]
    return list(reversed(path))


def bfs(graph: dict[str, list[str]], start: str, goal: str | None = None) -> dict[str, Any]:
    """BFS with FIFO queue, discovered-on-enqueue and alphabetical successors.

    A targeted search stops when the goal is removed from the queue.
    A full search (goal=None) visits every reachable vertex from start.
    """
    _check_search_inputs(graph, start, goal)
    queue = deque([start])
    discovered = {start}
    parents: dict[str, str | None] = {start: None}
    depths = {start: 0}  # True shortest-hop distance in the directed graph.
    order: list[str] = []
    steps: list[dict[str, Any]] = []

    while queue:
        current = queue.popleft()
        order.append(current)
        is_goal = goal is not None and current == goal
        if not is_goal:
            for neighbour in sorted(graph[current], key=lambda s: (s.casefold(), s)):
                if neighbour not in discovered:
                    discovered.add(neighbour)
                    parents[neighbour] = current
                    depths[neighbour] = depths[current] + 1
                    queue.append(neighbour)
        steps.append({
            "number": len(order), "expanded": current, "level": depths[current],
            "frontier": list(queue), "discovered": sorted(discovered),
            "visited": list(order), "parents": dict(parents),
        })
        if is_goal:
            break

    return {"algorithm": "BFS", "order": order, "steps": steps,
            "parents": parents, "depths": depths,
            "path": build_path(parents, goal), "goal_found": goal is None or goal in order}


def dfs(graph: dict[str, list[str]], start: str, goal: str | None = None) -> dict[str, Any]:
    """Recursive DFS with alphabetical successors and visited-set cycle safety.

    For DFS, `depths` are depths in the DFS discovery tree, NOT shortest-hop
    distances in the original graph. Each trace records the active call stack.
    """
    _check_search_inputs(graph, start, goal)
    discovered: set[str] = set()
    parents: dict[str, str | None] = {start: None}
    depths = {start: 0}
    order: list[str] = []
    steps: list[dict[str, Any]] = []

    def visit(current: str, active_stack: list[str]) -> bool:
        discovered.add(current)
        order.append(current)
        stack = active_stack + [current]
        steps.append({
            "number": len(order), "expanded": current, "level": depths[current],
            "frontier": stack, "discovered": sorted(discovered),
            "visited": list(order), "parents": dict(parents),
        })
        if goal is not None and current == goal:
            return True
        for neighbour in sorted(graph[current], key=lambda s: (s.casefold(), s)):
            if neighbour not in discovered:
                parents[neighbour] = current
                depths[neighbour] = depths[current] + 1
                if visit(neighbour, stack):
                    return True
        return False

    found = visit(start, [])
    return {"algorithm": "DFS", "order": order, "steps": steps,
            "parents": parents, "depths": depths,
            "path": build_path(parents, goal), "goal_found": goal is None or found}


def graph_dot(graph: dict[str, list[str]], start: str, snapshot: dict[str, Any] | None) -> str:
    """Create a DOT visualisation of the exact DIRECTED adjacency list."""
    from graphviz import Digraph

    dot = Digraph(comment="BSD3513 directed search graph", graph_attr={
        "rankdir": "LR", "bgcolor": "transparent", "pad": "0.28", "nodesep": "0.42",
        "ranksep": "0.76", "splines": "true", "fontname": "Helvetica"})
    dot.attr("node", shape="circle", style="filled", fontname="Helvetica",
             fontsize="15", width="0.56", color="#526278", penwidth="1.5")
    highlighted = set(snapshot["visited"]) if snapshot else set()
    current = snapshot["expanded"] if snapshot else None
    parent = snapshot["parents"] if snapshot else {}
    for node in graph:
        if node == current:
            fill, font = "#f9c74f", "#182434"
        elif node in highlighted:
            fill, font = "#2dd4bf", "#102e32"
        elif node == start:
            fill, font = "#f7bc66", "#182434"
        else:
            fill, font = "#e6edf5", "#26374a"
        dot.node(node, label=node, fillcolor=fill, fontcolor=font)
    for source, destinations in graph.items():
        for target in destinations:
            on_tree = target in highlighted and parent.get(target) == source
            dot.edge(source, target, color="#0e9f97" if on_tree else "#94a3b8",
                     penwidth="2.8" if on_tree else "1.35", arrowsize="0.8")
    return dot.source


def test_official_graph() -> None:
    """Reproducible deterministic checks against the original lab figure."""
    graph = normalize_graph(LAB_GRAPH)
    assert len(graph) == 8
    assert sum(len(v) for v in graph.values()) == 11
    assert bfs(graph, "A")["order"] == ["A", "B", "D", "C", "E", "G", "H", "F"]
    assert dfs(graph, "A")["order"] == ["A", "B", "C", "E", "H", "F", "G", "D"]
    assert bfs(graph, "A")["depths"] == {
        "A": 0, "B": 1, "D": 1, "C": 2, "E": 2, "G": 2, "H": 3, "F": 3}
    assert dfs(graph, "A")["depths"] == {
        "A": 0, "B": 1, "C": 2, "E": 2, "H": 3, "F": 4, "G": 4, "D": 1}
    assert bfs(graph, "A", "F")["path"] == ["A", "B", "G", "F"]
    assert dfs(graph, "A", "F")["path"] == ["A", "B", "E", "H", "F"]
    assert bfs(graph, "F", "A")["goal_found"] is False
    assert dfs(graph, "F", "A")["goal_found"] is False
    cyclic = normalize_graph({"Z": ["Y", "Y"], "Y": ["Z", "X"]})
    assert bfs(cyclic, "Z")["order"] == ["Z", "Y", "X"]
    assert dfs(cyclic, "Z")["order"] == ["Z", "Y", "X"]


def run_app() -> None:
    import streamlit as st

    st.set_page_config(page_title="BSD3513 | BFS & DFS Lab Explorer",
                       page_icon="🧭", layout="wide", initial_sidebar_state="expanded")
    st.markdown("""
    <style>
    .block-container {padding-top: 1.4rem; max-width: 1320px;}
    h1 {letter-spacing: -.025em;}
    .lab-subtitle {font-size:1.06rem;color:#64748b;margin-top:-.25rem;margin-bottom:1rem}
    .info-caption {font-size:.85rem;color:#64748b}
    div[data-testid="stMetric"] {border:1px solid rgba(125,145,165,.28);border-radius:13px;padding:10px 14px;}
    </style>
    """, unsafe_allow_html=True)
    st.title("BFS & DFS · Directed Graph Explorer")
    st.markdown('<div class="lab-subtitle">BSD3513 · Lab Report 1 · Original A–H graph from Question 2</div>',
                unsafe_allow_html=True)

    with st.sidebar:
        st.header("Experiment setup")
        input_mode = st.radio("Directed graph", ("Official lab graph (A–H)", "Custom graph (JSON)"))
        graph = normalize_graph(LAB_GRAPH)
        if input_mode == "Custom graph (JSON)":
            raw_json = st.text_area("Adjacency list", value=json.dumps(LAB_GRAPH, indent=2),
                                    height=260, help='Example: {"A":["B"],"B":[]}')
            try:
                graph = normalize_graph(json.loads(raw_json))
            except (ValueError, json.JSONDecodeError) as err:
                st.error(f"Cannot read graph: {err}")
                st.stop()
        nodes = list(graph)
        start = st.selectbox("Starting node", nodes, index=nodes.index("A") if "A" in nodes else 0)
        goal_option = st.selectbox("Goal (optional)", ["Full traversal (no goal)"] + nodes)
        goal = None if goal_option == "Full traversal (no goal)" else goal_option
        algorithm = st.radio("Algorithm", ("BFS", "DFS"), horizontal=True)
        st.caption("Alphabetical tie-breaking is applied to outgoing neighbours. All edges are directed.")
        if input_mode.startswith("Official"):
            st.info("The lab diagram does not name a start node. We explicitly assume A; change it here if instructed by your lecturer.")

    result = bfs(graph, start, goal) if algorithm == "BFS" else dfs(graph, start, goal)
    comparator = dfs(graph, start, goal) if algorithm == "BFS" else bfs(graph, start, goal)
    visited_count = len(result["order"])
    total_nodes = len(graph)
    edges_count = sum(map(len, graph.values()))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Directed nodes", total_nodes)
    c2.metric("Directed edges", edges_count)
    c3.metric("Expanded nodes", visited_count)
    c4.metric("Maximum discovery depth", max(result["depths"].values()))

    graph_tab, trace_tab, compare_tab, theory_tab = st.tabs([
        "Graph simulation", "Full search trace", "BFS vs DFS", "Theory & references"])
    with graph_tab:
        st.markdown("#### Interactive traversal")
        n_steps = len(result["steps"])
        chosen_step = st.slider("Replay expansion step", min_value=0, max_value=n_steps,
                                value=n_steps, step=1, help="0 = graph before search; the final step = completed traversal")
        snapshot = result["steps"][chosen_step - 1] if chosen_step > 0 else None
        left, right = st.columns([1.45, 1.0], gap="large")
        with left:
            st.graphviz_chart(graph_dot(graph, start, snapshot), use_container_width=True)
            st.caption("Orange = starting node · Gold = node currently expanded · Teal = previously expanded · Light = not yet expanded. Teal arrows show discovered parent edges.")
        with right:
            st.subheader(f"{algorithm} processing order")
            shown = snapshot["visited"] if snapshot else []
            st.code(" → ".join(shown) if shown else "Not started", language="text")
            if snapshot:
                st.write(f"**Current node:** {snapshot['expanded']}")
                st.write(f"**{'Queue (front → back)' if algorithm == 'BFS' else 'Active recursion stack'}:** " +
                         (" → ".join(snapshot["frontier"]) or "Empty"))
                st.write(f"**Node discovery depth:** {snapshot['level']}")
            else:
                st.info("Move the slider to expand the first node.")
            if chosen_step == n_steps:
                if goal is None:
                    st.success("Full reachable traversal complete.")
                elif result["goal_found"]:
                    st.success("Goal reached. Search-tree path: " + " → ".join(result["path"]))
                    st.caption(f"Number of path edges: {len(result['path']) - 1}")
                else:
                    st.warning("Goal is not reachable from the selected starting node.")
            st.caption("A traversal sequence is the expansion order; it is not necessarily a valid directed path between consecutive nodes.")

        levels: dict[int, list[str]] = {}
        for node in result["order"]:
            levels.setdefault(result["depths"][node], []).append(node)
        st.markdown("#### " + ("BFS shortest-hop levels" if algorithm == "BFS" else "DFS discovery-tree depths"))
        st.table([{"Level / Depth": depth, "Nodes in discovery order": ", ".join(groups)}
                  for depth, groups in sorted(levels.items())])
        if algorithm == "DFS":
            st.caption("DFS depth comes from the DFS discovery tree; it need not be the minimum-hop level in the directed graph.")

    with trace_tab:
        st.markdown("#### Step-by-step expansion trace")
        st.dataframe([{
            "Step": step["number"],
            "Expanded": step["expanded"],
            "Depth": step["level"],
            "Frontier after step" if algorithm == "BFS" else "Active DFS stack": " → ".join(step["frontier"]) or "Empty",
            "Visited (expansion order)": " → ".join(step["visited"]),
        } for step in result["steps"]], use_container_width=True, hide_index=True)
        st.markdown("#### Adjacency list (outgoing directed edges only)")
        st.code(json.dumps(graph, indent=2), language="json")
        st.download_button("Download traversal trace (JSON)",
                           data=json.dumps({"start": start, "goal": goal, "graph": graph,
                                            "algorithm": algorithm, "result": result}, indent=2),
                           file_name=f"{algorithm.lower()}_lab1_trace.json", mime="application/json")

    with compare_tab:
        st.markdown("#### Compare both search methods on exactly the same graph")
        all_results = {result["algorithm"]: result, comparator["algorithm"]: comparator}
        st.table([{"Algorithm": key,
                   "Expansion order": " → ".join(all_results[key]["order"]),
                   "Expanded": len(all_results[key]["order"]),
                   "Goal path": " → ".join(all_results[key]["path"]) if goal else "Not specified"}
                  for key in ("BFS", "DFS")])
        st.info("BFS finds fewest edges in an unweighted directed graph. DFS follows depth-first exploration and does not guarantee a minimum-edge path.")
        if input_mode.startswith("Official") and start == "A" and goal is None:
            st.caption("Expected official-graph outputs from start A: BFS = A B D C E G H F; DFS = A B C E H F G D.")

    with theory_tab:
        st.markdown("#### Theory used for this lab")
        st.write("**BFS:** expands all neighbours at the current distance before the next level. A FIFO queue records pending nodes. (Chapter 2, slides 20–22.)")
        st.write("**DFS:** recursively follows each available branch to maximum depth, then backtracks. The active recursion stack tracks its search path. (Chapter 2, slides 25–27.)")
        st.write("**Implementation complexity:** both run in **O(V + E)** time for adjacency lists and a visited set; worst-case auxiliary storage is **O(V)** for BFS queue or DFS recursion and visited tracking. This complexity is derived for the implementation shown here.")
        st.write("**Cycle safety:** nodes are marked discovered when first enqueued or entered, so directed cycles (for example C → A) cannot cause endless revisits.")
        st.markdown("#### Source materials")
        st.caption("Ku Muhammad Na'im Ku Khalif, Chapter 2: Search Algorithms, BSD3513 lecture slides, slides 19–27; BSD3513 Lab Report 1, page 2; lecturer-provided bfs_simple.py and dfs_simple.py. No external graph was substituted.")
        st.warning("Before submission: publish this exact file to GitHub and deploy it. Add your REAL verified URLs to the PDF report; none are generated automatically by this local app.")
    st.divider()
    st.caption("BSD3513 • Lab Report 1 • Deterministic directed traversal • Student ID: SD24057")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        test_official_graph()
        print("PASS: 12 official/cycle checks, including traversal, levels and goal paths.")
    else:
        run_app()
