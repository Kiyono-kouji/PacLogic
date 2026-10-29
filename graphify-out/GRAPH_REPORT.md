# Graph Report - PacLogicV2  (2026-10-30)

## Corpus Check
- 35 files · ~8,391 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: .aseprite 5, (none) 1, .ttf 1)

## Summary
- 318 nodes · 827 edges · 15 communities (12 shown, 3 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 65 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b7a5f870`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- blocks.py
- Label
- MapView
- BaseScene
- Level
- load_font
- Sim
- Board
- .__init__
- resource_loader.py
- Session
- ProgramEditor
- PreviewScene
- PlayScene
- .__init__

## God Nodes (most connected - your core abstractions)
1. `Level` - 42 edges
2. `Label` - 28 edges
3. `Session` - 23 edges
4. `Board` - 23 edges
5. `ProgramEditor` - 23 edges
6. `BaseScene` - 22 edges
7. `Button` - 22 edges
8. `Component` - 21 edges
9. `MenuScene` - 19 edges
10. `Panel` - 19 edges

## Surprising Connections (you probably didn't know these)
- `load_font()` --conceptually_related_to--> `pygame-ce >= 2.5 dependency`  [INFERRED]
  src/core/resource_loader.py → requirements.txt
- `load_level()` --shares_data_with--> `Easy level map (15x11, 4 ghosts, 3 pellets)`  [INFERRED]
  src/logic/grid.py → assets/levels/easy.txt
- `load_level()` --shares_data_with--> `Hard level map (21x15, 4 ghosts, 9 pellets)`  [INFERRED]
  src/logic/grid.py → assets/levels/hard.txt
- `load_level()` --shares_data_with--> `Medium level map (19x13, 4 ghosts, 5 pellets)`  [INFERRED]
  src/logic/grid.py → assets/levels/medium.txt
- `load_font()` --shares_data_with--> `Jersey 10 font (Soft Type Project, 2023)`  [INFERRED]
  src/core/resource_loader.py → assets/fonts/Jersey10-OFL.txt

## Import Cycles
- 4-file cycle: `src/scenes/menu_scene.py -> src/scenes/preview_scene.py -> src/scenes/plan_scene.py -> src/scenes/play_scene.py -> src/scenes/menu_scene.py`
- 4-file cycle: `src/scenes/plan_scene.py -> src/scenes/play_scene.py -> src/scenes/result_scene.py -> src/scenes/preview_scene.py -> src/scenes/plan_scene.py`
- 5-file cycle: `src/scenes/menu_scene.py -> src/scenes/preview_scene.py -> src/scenes/plan_scene.py -> src/scenes/play_scene.py -> src/scenes/result_scene.py -> src/scenes/menu_scene.py`

## Hyperedges (group relationships)
- **Hand-made level set (easy, medium, hard) in the shared text format** — assets_levels_easy_level, assets_levels_medium_level, assets_levels_hard_level, assets_levels_easy_level_text_format [EXTRACTED 1.00]

## Communities (15 total, 3 thin omitted)

### Community 0 - "blocks.py"
Cohesion: 0.16
Nodes (11): check_programs(), controllers_for(), play_rounds(), programs_for(), _clamp_count(), depth_range(), _execute(), parse() (+3 more)

### Community 1 - "Label"
Cohesion: 0.12
Nodes (15): pygame, Event, Surface, ResultScene, Button, Event, Component, Event (+7 more)

### Community 2 - "MapView"
Cohesion: 0.27
Nodes (5): fit_tile_size(), MapView, Font, Rect, Surface

### Community 3 - "BaseScene"
Cohesion: 0.10
Nodes (8): Game, BaseScene, Event, Surface, MenuScene, cycle(), Event, Surface

### Community 4 - "Level"
Cohesion: 0.12
Nodes (29): collections, dataclasses, pathlib, breadth_first(), distance_table(), maze_heuristic(), plan_bfs(), PacManBrain (+21 more)

### Community 5 - "load_font"
Cohesion: 0.15
Nodes (13): Jersey 10 font (Soft Type Project, 2023), SIL Open Font License 1.1, PacLogic README, pygame-ce >= 2.5 dependency, load_font(), Font, block_kind(), block_rect() (+5 more)

### Community 6 - "Sim"
Cohesion: 0.18
Nodes (17): Easy level map (15x11, 4 ghosts, 3 pellets), Level text format (# wall, . floor, P start, E exit, G ghost, o pellet), Hard level map (21x15, 4 ghosts, 9 pellets), Medium level map (19x13, 4 ghosts, 5 pellets), Path, check_corridor_same_tile(), check_corridor_tile_swap(), check_headless_run() (+9 more)

### Community 7 - "Board"
Cohesion: 0.12
Nodes (8): PlanScene, Event, Surface, Board, Rect, Surface, FlashMessage, Surface

### Community 9 - "resource_loader.py"
Cohesion: 0.14
Nodes (11): functools, animation_frame(), load_sprite(), Surface, sprite_size(), Character, Surface, Enemy (+3 more)

### Community 11 - "ProgramEditor"
Cohesion: 0.25
Nodes (3): ProgramEditor, Event, Surface

### Community 12 - "PreviewScene"
Cohesion: 0.20
Nodes (4): PreviewScene, Event, Rect, Surface

### Community 13 - "PlayScene"
Cohesion: 0.24
Nodes (3): PlayScene, Event, Surface

## Ambiguous Edges - Review These
- `Jersey 10 font (Soft Type Project, 2023)` → `PacLogic README`  [AMBIGUOUS]
  README.md · relation: references

## Knowledge Gaps
- **3 isolated node(s):** `pygame-ce >= 2.5 dependency`, `SIL Open Font License 1.1`, `PacLogic README`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 76 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Jersey 10 font (Soft Type Project, 2023)` and `PacLogic README`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `Level` connect `Level` to `blocks.py`, `Label`, `MapView`, `Sim`, `Board`, `Session`?**
  _High betweenness centrality (0.224) - this node is a cross-community bridge._
- **Why does `Board` connect `Board` to `Label`, `MapView`, `Level`, `resource_loader.py`, `PreviewScene`, `PlayScene`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Why does `ProgramEditor` connect `ProgramEditor` to `Label`, `Board`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Level` (e.g. with `Session` and `distance_table()`) actually correct?**
  _`Level` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `Label` (e.g. with `MenuScene` and `PlanScene`) actually correct?**
  _`Label` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Session` (e.g. with `Game` and `PacManBrain`) actually correct?**
  _`Session` has 4 INFERRED edges - model-reasoned connections that need verification._