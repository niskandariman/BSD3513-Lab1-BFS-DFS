# BSD3513 Lab Report 1 — BFS & DFS Directed Graph Explorer

## Project Overview

This project is developed for **BSD3513: Introduction to Artificial Intelligence**, Lab Report 1, at Universiti Malaysia Pahang Al-Sultan Abdullah (UMPSA).

The application demonstrates Breadth-First Search (BFS) and Depth-First Search (DFS) using Python and Streamlit. It allows users to explore directed graphs and understand how both search algorithms traverse nodes.

## Student Information

- **Name:** NOR ISKANDAR IMAN BIN NOORAZLIND
- **Student ID:** SD24057
- **Course:** BSD3513 — Introduction to Artificial Intelligence
- **Institution:** Universiti Malaysia Pahang Al-Sultan Abdullah (UMPSA)

## Features

- Interactive visualization of directed graphs
- Breadth-First Search (BFS) using a FIFO queue
- Depth-First Search (DFS) using recursive traversal
- Alphabetical tie-breaking when expanding adjacent nodes
- Step-by-step traversal visualization
- Starting node and optional goal selection
- Traversal order and discovery-depth information
- Comparison of BFS and DFS
- Support for custom directed graphs using JSON input

## Search Algorithms

### Breadth-First Search (BFS)

BFS explores nodes level by level using a queue. In an unweighted graph, BFS can find the shortest path in terms of the number of edges.

**Traversal order for the official lab graph (starting at A):**

`A → B → D → C → E → G → H → F`

### Depth-First Search (DFS)

DFS explores one branch as deeply as possible before backtracking. This application uses recursive DFS.

**Traversal order for the official lab graph (starting at A):**

`A → B → C → E → H → F → G → D`

Both algorithms use alphabetical tie-breaking when multiple outgoing neighbours are available.

## Technologies Used

- Python
- Streamlit
- Graphviz
- GitHub
- Streamlit Community Cloud

## Installation and Usage

1. Clone the repository:

   `git clone https://github.com/niskandariman/BSD3513-Lab1-BFS-DFS.git`

2. Navigate to the project folder:

   `cd BSD3513-Lab1-BFS-DFS`

3. Install dependencies:

   `python -m pip install -r requirements.txt`

4. Run the Streamlit application:

   `python -m streamlit run SD24057_Lab1.py`

5. Open `http://localhost:8501` in your browser.

## Live Application

**Streamlit App:** https://bsd3513-lab1-bfs-dfs.streamlit.app

**GitHub Repository:** https://github.com/niskandariman/BSD3513-Lab1-BFS-DFS



## Academic Purpose

This project was developed for educational purposes to demonstrate the application of uninformed search algorithms, graph traversal, and interactive visualization in artificial intelligence.
