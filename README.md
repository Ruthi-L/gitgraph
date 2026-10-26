# GitGraph // GitHub Network & Interaction Analyzer

---

## Tech Stack
* **Backend:** Python, Flask, SQLite
* **Graph & Data Processing:** NetworkX, PyVis, GitHub REST API
* **Algorithms:** Custom Breadth-First Search (BFS) shortest path, Connected Component clustering
* **Frontend & Styling:** Tailwind CSS, HTML5, Minimalist Editorial UI Design

---

## Core Architecture & DSA Engine (`dsa.py`)
Unlike standard apps relying on black-box external libraries for graph traversal, this project implements core graph algorithms from scratch:
1. **Custom BFS Shortest Path:** Computes the exact shortest degree of separation (interaction chain) between any two developers in the network.
2. **Connected Component Isolation:** Traverses the graph structure to isolate distinct developer interaction communities.
3. **Dynamic Graph Styling:** Automatically injects node and edge highlighting attributes into the topology canvas when a shortest path is calculated.

---
## Key Features

**Profile Scraper**: Safely indexes public followers, repositories, stargazers, and forkers via the GitHub REST API (rate-limit safe with token support).

**Interactive Topology Canvas**: Clean vis.js graph rendering with custom color-coded interaction edges (Follows, Starred, Forked) and automated loading bar suppression.

**Live Metrics Ticker**: Real-time calculation of total indexed developer nodes, relationship edges, and community clusters.

## 🚀 Getting Started Locally

1. Clone the Repository
```bash
git clone [https://github.com/Ruthi-L/gitgraph.git](https://github.com/Ruthi-L/gitgraph.git)
cd gitgraph

 2. Install Dependencies
Bash
pip install flask networkx pyvis requests

3. Run the Application
Bash
python app.py