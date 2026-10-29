# Graph Report - PacLogicV2  (2026-10-28)

## Corpus Check
- 26 files · ~6,212 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .ttf 1)

## Summary
- 220 nodes · 493 edges · 11 communities (10 shown, 1 thin omitted)
- Extraction: 93% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d36ea4db`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- grid.py
- Component
- MapView
- BaseScene
- Level
- Jersey 10 font (Soft Type Project, 2023)
- blocks.py
- .draw
- Button
- Character
- ProgramEditor

## God Nodes (most connected - your core abstractions)
1. `Level` - 36 edges
2. `Component` - 19 edges
3. `ProgramEditor` - 19 edges
4. `Sim` - 15 edges
5. `BaseScene` - 13 edges
6. `plan()` - 11 edges
7. `load_font()` - 10 edges
8. `parse_level()` - 10 edges
9. `SearchResult` - 10 edges
10. `MapView` - 10 edges

## Surprising Connections (you probably didn't know these)
- `load_font()` --shares_data_with--> `Jersey 10 font (Soft Type Project, 2023)`  [INFERRED]
  src/core/resource_loader.py → assets/fonts/Jersey10-OFL.txt
- `load_font()` --conceptually_related_to--> `pygame-ce >= 2.5 dependency`  [INFERRED]
  src/core/resource_loader.py → requirements.txt
- `parse_level()` --implements--> `Level text format (# wall, . floor, P start, E exit, G ghost, o pellet)`  [INFERRED]
  src/logic/grid.py → assets/levels/easy.txt
- `load_level()` --shares_data_with--> `Easy level map (15x11, 4 ghosts, 3 pellets)`  [INFERRED]
  src/logic/grid.py → assets/levels/easy.txt
- `load_level()` --shares_data_with--> `Hard level map (21x15, 4 ghosts, 9 pellets)`  [INFERRED]
  src/logic/grid.py → assets/levels/hard.txt

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Hand-made level set (easy, medium, hard) in the shared text format** — assets_levels_easy_level, assets_levels_medium_level, assets_levels_hard_level, assets_levels_easy_level_text_format [EXTRACTED 1.00]

## Communities (11 total, 1 thin omitted)

### Community 0 - "grid.py"
Cohesion: 0.16
Nodes (20): Easy level map (15x11, 4 ghosts, 3 pellets), Level text format (# wall, . floor, P start, E exit, G ghost, o pellet), Hard level map (21x15, 4 ghosts, 9 pellets), Medium level map (19x13, 4 ghosts, 5 pellets), collections, dataclasses, functools, Path (+12 more)

### Community 1 - "Component"
Cohesion: 0.09
Nodes (18): Font, pygame, pygame-ce >= 2.5 dependency, load_font(), block_kind(), block_rect(), draw_block(), draw_program() (+10 more)

### Community 2 - "MapView"
Cohesion: 0.35
Nodes (4): fit_tile_size(), MapView, Rect, Surface

### Community 3 - "BaseScene"
Cohesion: 0.12
Nodes (7): Game, _PlaceholderScene, Event, Surface, BaseScene, Event, Surface

### Community 4 - "Level"
Cohesion: 0.18
Nodes (19): breadth_first(), distance_table(), maze_heuristic(), plan_bfs(), PacManBrain, Level, manhattan(), best_first() (+11 more)

### Community 5 - "Jersey 10 font (Soft Type Project, 2023)"
Cohesion: 0.67
Nodes (3): Jersey 10 font (Soft Type Project, 2023), SIL Open Font License 1.1, PacLogic README

### Community 6 - "blocks.py"
Cohesion: 0.12
Nodes (17): check_corridor_same_tile(), check_corridor_tile_swap(), check_headless_run(), check_scoring(), ghost_controller(), main(), TestBrain, _clamp_count() (+9 more)

### Community 8 - "Button"
Cohesion: 0.32
Nodes (4): Button, Event, Rect, Surface

### Community 9 - "Character"
Cohesion: 0.15
Nodes (7): Character, lerp_tile(), Surface, Enemy, Surface, Player, Surface

### Community 11 - "ProgramEditor"
Cohesion: 0.18
Nodes (6): Panel, Rect, Surface, ProgramEditor, Event, Surface

## Ambiguous Edges - Review These
- `Jersey 10 font (Soft Type Project, 2023)` → `PacLogic README`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **3 isolated node(s):** `pygame-ce >= 2.5 dependency`, `SIL Open Font License 1.1`, `PacLogic README`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 45 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Jersey 10 font (Soft Type Project, 2023)` and `PacLogic README`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Component` connect `Component` to `Button`, `ProgramEditor`, `MapView`, `BaseScene`?**
  _High betweenness centrality (0.267) - this node is a cross-community bridge._
- **Why does `Level` connect `Level` to `grid.py`, `Component`, `MapView`, `blocks.py`?**
  _High betweenness centrality (0.203) - this node is a cross-community bridge._
- **Why does `ProgramEditor` connect `ProgramEditor` to `Component`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `Level` (e.g. with `distance_table()` and `maze_heuristic()`) actually correct?**
  _`Level` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ProgramEditor` (e.g. with `FlashMessage` and `Panel`) actually correct?**
  _`ProgramEditor` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `Sim` (e.g. with `run()` and `Level`) actually correct?**
  _`Sim` has 2 INFERRED edges - model-reasoned connections that need verification._