# GitGraph — GitHub Network & Interaction Analyzer

A full-stack tool that maps a GitHub user's social and repository network — followers, stargazers, and forkers — as an interactive, explorable graph. Built with a hand-implemented graph engine rather than relying solely on library defaults for traversal.

**Live demo:** https://gitgraph.onrender.com/
*(hosted on Render's free tier — the app may take 30–60 seconds to wake up on first load)*

---

## What it does

1. Enter any public GitHub username.
2. GitGraph fetches that user's followers, repositories, stargazers, and forkers via the GitHub REST API.
3. The relationships are stored and modeled as a directed graph (`FOLLOWS`, `STARRED`, `FORKED` edges).
4. The graph renders as an interactive, color-coded network you can explore — zoom, drag nodes, and inspect individual relationships.
5. Select any two developers in the network to compute the shortest interaction path (degree of separation) between them.

---

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Graph & Data Processing:** NetworkX, PyVis, GitHub REST API
- **Algorithms:** Custom BFS shortest-path, custom connected-component clustering
- **Frontend:** HTML5, Tailwind CSS

---

## Core Architecture — `dsa.py`

The graph traversal logic is implemented directly, rather than calling a library's built-in traversal functions end-to-end:

- **BFS Shortest Path** — computes the exact shortest degree of separation between any two developers in the network by traversing the adjacency structure manually.
- **Connected Component Isolation** — traverses the graph to identify and group distinct developer interaction clusters.
- **Dynamic Graph Styling** — when a shortest path is computed, the relevant nodes and edges are highlighted on the canvas to visually trace the path.

---

## Key Features

- **Profile Scraper** — indexes a user's public followers, repositories, stargazers, and forkers via the GitHub REST API.
- **Interactive Topology Canvas** — PyVis/vis.js rendering with color-coded edges by interaction type (Follows, Starred, Forked).
- **Live Metrics** — displays the current count of indexed developer nodes, relationship edges, and detected clusters.

---

## Getting Started Locally

### 1. Clone the repository

```bash
git clone https://github.com/Ruthi-L/gitgraph.git
cd gitgraph
```

### 2. Install dependencies

```bash
pip install flask networkx pyvis requests
```

### 3. Run the application

```bash
python app.py
```

The app will be available at `http://localhost:5005`.

---

## Why build the graph algorithms from scratch?

NetworkX already ships BFS and connected-component functions, and using them directly would have worked fine. The traversal and clustering logic here is implemented manually instead, as a deliberate choice to work through the graph theory directly — adjacency structures, visited-node tracking, and path reconstruction — rather than only calling a library function.