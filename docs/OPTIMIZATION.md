# Optimization Methodology

This document explains the mini rescue and relief optimizer built into the RAHAT system.

## Problem Definition
During a flood emergency, resources (boats, medical teams) are limited, and time is critical. The commander must know:
1. Who needs help the most?
2. What is the fastest way to reach them?
3. What happens if a critical road washes away?

## Decision Variables
- **Target Habitation:** Selected based on the highest priority score (a combination of hazard class and affected population).
- **Route Selection:** The physical path taken from the Relief Base to the Target Habitation.

## Objective Function
The primary objective of this prototype's heuristic solver is to **minimize response time** (and distance) to the highest priority mission while navigating physical constraints (road closures).

## Methodology: Dijkstra's Algorithm
The system relies on a NetworkX-style graph representation, solved via a custom Python priority-queue implementation of Dijkstra's Algorithm (`src/optimization/solver.py`).

1. **Base Scenario:** The algorithm searches the full graph to find the path with the minimum accumulated distance from the `base_jonai` node to the target habitation node.
2. **Disruption Scenario:** We simulate a road closure (e.g., a submerged bridge) by identifying a critical edge in the base path and removing it from the graph.
3. **Re-optimization:** The algorithm runs again on the restricted graph, finding the next-best alternative route.

## Output Metrics
The script calculates the estimated travel time (assuming 20 km/h in flood conditions) and outputs the results to `public/data/optimization_scenario.json`.

The TypeScript dashboard instantly visualizes these two states (Base vs Re-routed) on the map and displays the exact time penalty (+X hours) incurred by the road closure.
