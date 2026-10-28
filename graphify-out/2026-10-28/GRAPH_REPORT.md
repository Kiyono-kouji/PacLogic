# Graph Report - PacLogic  (2026-10-28)

## Corpus Check
- Corpus is ~2,084 words - fits in a single context window. You may not need a graph.

## Summary
- 61 nodes · 127 edges · 6 communities (5 shown, 1 thin omitted)
- Extraction: 86% EXTRACTED · 13% INFERRED · 1% AMBIGUOUS · INFERRED: 17 edges (avg confidence: 0.88)
- Token cost: 64,772 input · 0 output

## Community Hubs (Navigation)
- Level Model and BFS
- Module Imports and Helpers
- Map View Rendering
- BFS Search and Heuristic
- Level Files and Parsing
- Font and Project Docs

## God Nodes (most connected - your core abstractions)
1. `Level` - 22 edges
2. `bfs_dist()` - 10 edges
3. `_pick_ghosts()` - 10 edges
4. `MapView` - 9 edges
5. `validate_level()` - 8 edges
6. `load_level()` - 8 edges
7. `generate_level()` - 7 edges
8. `LevelError` - 5 edges
9. `parse_level()` - 5 edges
10. `load_font()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `load_level()` --shares_data_with--> `Easy level map (15x11, 4 ghosts, 3 pellets)`  [INFERRED]
  src/logic/grid.py → assets/levels/easy.txt
- `load_level()` --shares_data_with--> `Hard level map (21x15, 4 ghosts, 9 pellets)`  [INFERRED]
  src/logic/grid.py → assets/levels/hard.txt
- `load_level()` --shares_data_with--> `Medium level map (19x13, 4 ghosts, 5 pellets)`  [INFERRED]
  src/logic/grid.py → assets/levels/medium.txt
- `load_font()` --shares_data_with--> `Jersey 10 font (Soft Type Project, 2023)`  [INFERRED]
  src/core/resource_loader.py → assets/fonts/Jersey10-OFL.txt
- `load_font()` --conceptually_related_to--> `pygame-ce >= 2.5 dependency`  [INFERRED]
  src/core/resource_loader.py → requirements.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Hand-made level set (easy, medium, hard) in the shared text format** — assets_levels_easy_level, assets_levels_medium_level, assets_levels_hard_level, assets_levels_easy_level_text_format [EXTRACTED 1.00]

## Communities (6 total, 1 thin omitted)

### Community 0 - "Level Model and BFS"
Cohesion: 0.37
Nodes (7): bfs_dist(), generate_level(), Level, move(), _pick_ghosts(), _route_tiles(), validate_level()

### Community 1 - "Module Imports and Helpers"
Cohesion: 0.24
Nodes (3): _carve_maze(), _farthest(), manhattan()

### Community 3 - "BFS Search and Heuristic"
Cohesion: 0.29
Nodes (4): breadth_first(), distance_table(), maze_heuristic(), plan_bfs()

### Community 4 - "Level Files and Parsing"
Cohesion: 0.31
Nodes (7): Easy level map (15x11, 4 ghosts, 3 pellets), Level text format (# wall, . floor, P start, E exit, G ghost, o pellet), Hard level map (21x15, 4 ghosts, 9 pellets), Medium level map (19x13, 4 ghosts, 5 pellets), LevelError, load_level(), parse_level()

### Community 5 - "Font and Project Docs"
Cohesion: 0.33
Nodes (5): Jersey 10 font (Soft Type Project, 2023), SIL Open Font License 1.1, PacLogic README, pygame-ce >= 2.5 dependency, load_font()

## Ambiguous Edges - Review These
- `PacLogic README` → `Jersey 10 font (Soft Type Project, 2023)`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **3 isolated node(s):** `PacLogic README`, `pygame-ce >= 2.5 dependency`, `SIL Open Font License 1.1`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 10 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Level` connect `Level Model and BFS` to `Module Imports and Helpers`, `Map View Rendering`, `BFS Search and Heuristic`, `Level Files and Parsing`?**
  _High betweenness centrality (0.420) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Level` (e.g. with `distance_table()` and `maze_heuristic()`) actually correct?**
  _`Level` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `PacLogic README`, `pygame-ce >= 2.5 dependency`, `SIL Open Font License 1.1` to the rest of the system?**
  _3 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `MapView` connect `Map View Rendering` to `Level Model and BFS`, `Module Imports and Helpers`?**
  _High betweenness centrality (0.195) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `_pick_ghosts()` (e.g. with `.floor_tiles()` and `.safe_zone()`) actually correct?**
  _`_pick_ghosts()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Why does `load_font()` connect `Font and Project Docs` to `Module Imports and Helpers`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `PacLogic README` and `Jersey 10 font (Soft Type Project, 2023)`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._