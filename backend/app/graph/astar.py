"""
A* algorithm for optimal path finding with heuristics
"""
import heapq
import math
from typing import Dict, List, Tuple, Optional, Callable
from app.graph.graph_builder import CampusGraph

class AStarRouter:
    """
    Implements A* algorithm for optimal path finding with heuristic
    """
    
    def __init__(self, graph: CampusGraph):
        self.graph = graph
    
    def heuristic(self, node_id: int, goal_id: int) -> float:
        """
        Calculate heuristic distance (straight-line distance)
        Uses simple Euclidean distance on lat/lon
        """
        node = self.graph.get_location(node_id)
        goal = self.graph.get_location(goal_id)
        
        if not node or not goal:
            return 0
        
        # Simple distance calculation (not exact, but good heuristic)
        lat_diff = node['latitude'] - goal['latitude']
        lon_diff = node['longitude'] - goal['longitude']
        
        # Approximate meters per degree
        meters_per_degree = 111320
        
        distance = math.sqrt((lat_diff ** 2 + lon_diff ** 2)) * meters_per_degree
        return distance
    
    def find_path(
        self,
        start_id: int,
        end_id: int,
        weight_key: str = "walking_time",
        avoid_blocked: bool = True,
        accessibility_required: bool = False
    ) -> Dict:
        """
        Find optimal path using A* algorithm
        
        Args:
            start_id: Starting location ID
            end_id: Destination location ID
            weight_key: Which edge weight to optimize (walking_time, distance)
            avoid_blocked: Whether to avoid blocked routes
            accessibility_required: Whether to only use accessible routes
        
        Returns:
            Dictionary with path, distance, time, and metadata
        """
        
        if not self.graph.is_valid_node(start_id) or not self.graph.is_valid_node(end_id):
            return {"error": "Invalid location"}
        
        # Initialize
        g_score = {node_id: float('inf') for node_id in self.graph.nodes}
        g_score[start_id] = 0
        
        f_score = {node_id: float('inf') for node_id in self.graph.nodes}
        f_score[start_id] = self.heuristic(start_id, end_id)
        
        previous = {node_id: None for node_id in self.graph.nodes}
        visited = set()
        edge_info = {}
        
        # Priority queue: (f_score, counter, node_id)
        counter = 0
        pq = [(f_score[start_id], counter, start_id)]
        
        while pq:
            _, _, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Early termination
            if current_node == end_id:
                break
            
            # Check neighbors
            for neighbor_id, edge_data in self.graph.get_neighbors(current_node):
                # Skip blocked routes
                if avoid_blocked and edge_data.get('is_blocked', False):
                    continue
                
                # Skip if accessibility required
                if accessibility_required and not edge_data.get('is_wheelchair_accessible', False):
                    continue
                
                # Calculate new g_score
                weight = edge_data.get(weight_key, float('inf'))
                tentative_g = g_score[current_node] + weight
                
                if tentative_g < g_score[neighbor_id]:
                    # Found a better path
                    previous[neighbor_id] = current_node
                    edge_info[neighbor_id] = edge_data
                    g_score[neighbor_id] = tentative_g
                    f_score[neighbor_id] = tentative_g + self.heuristic(neighbor_id, end_id)
                    
                    counter += 1
                    heapq.heappush(pq, (f_score[neighbor_id], counter, neighbor_id))
        
        # Reconstruct path
        path = []
        current = end_id
        
        if previous[current] is None and current != start_id:
            return {"error": "No path found"}
        
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        
        # Calculate totals from the exact edges chosen by the algorithm.
        total_distance = 0
        total_time = 0
        route_ids = []
        
        for node_id in path[1:]:
            edge_data = edge_info.get(node_id, {})
            total_distance += edge_data.get('distance', 0)
            total_time += edge_data.get('walking_time', 0)
            if edge_data.get('route_id') is not None:
                route_ids.append(edge_data.get('route_id'))
        
        return {
            "path": path,
            "distance": total_distance,
            "walking_time": total_time,
            "route_ids": route_ids,
            "num_stops": len(path),
            "start_location": self.graph.get_location(start_id),
            "end_location": self.graph.get_location(end_id),
            "algorithm": "a_star",
            "mode": "shortest_time" if weight_key == "walking_time" else "shortest_distance"
        }
    
    def find_low_crowd_path(
        self,
        start_id: int,
        end_id: int,
        max_crowd_tolerance: float = 0.7
    ) -> Dict:
        """
        Find path avoiding crowded routes using A*
        """
        if not self.graph.is_valid_node(start_id) or not self.graph.is_valid_node(end_id):
            return {"error": "Invalid location"}
        
        g_score = {node_id: float('inf') for node_id in self.graph.nodes}
        g_score[start_id] = 0
        
        f_score = {node_id: float('inf') for node_id in self.graph.nodes}
        f_score[start_id] = self.heuristic(start_id, end_id)
        
        previous = {node_id: None for node_id in self.graph.nodes}
        visited = set()
        edge_info = {}
        
        counter = 0
        pq = [(f_score[start_id], counter, start_id)]
        
        while pq:
            _, _, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node == end_id:
                break
            
            for neighbor_id, edge_data in self.graph.get_neighbors(current_node):
                if edge_data.get('is_blocked', False):
                    continue
                
                # Penalize crowded routes
                crowdedness = edge_data.get('crowdedness_score', 0)
                crowd_penalty = 0
                
                if crowdedness > max_crowd_tolerance:
                    crowd_penalty = (crowdedness - max_crowd_tolerance) * 1000
                
                weight = edge_data.get('walking_time', float('inf')) + crowd_penalty
                tentative_g = g_score[current_node] + weight
                
                if tentative_g < g_score[neighbor_id]:
                    previous[neighbor_id] = current_node
                    edge_info[neighbor_id] = edge_data
                    g_score[neighbor_id] = tentative_g
                    f_score[neighbor_id] = tentative_g + self.heuristic(neighbor_id, end_id)
                    
                    counter += 1
                    heapq.heappush(pq, (f_score[neighbor_id], counter, neighbor_id))
        
        # Reconstruct path
        path = []
        current = end_id
        
        if previous[current] is None and current != start_id:
            return {"error": "No path found"}
        
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        
        # Calculate totals from the exact edges chosen by the algorithm.
        total_distance = 0
        total_time = 0
        avg_crowdedness = 0
        route_ids = []
        
        for node_id in path[1:]:
            edge_data = edge_info.get(node_id, {})
            total_distance += edge_data.get('distance', 0)
            total_time += edge_data.get('walking_time', 0)
            avg_crowdedness += edge_data.get('crowdedness_score', 0)
            if edge_data.get('route_id') is not None:
                route_ids.append(edge_data.get('route_id'))
        
        if len(path) > 1:
            avg_crowdedness /= (len(path) - 1)
        
        return {
            "path": path,
            "distance": total_distance,
            "walking_time": total_time,
            "route_ids": route_ids,
            "num_stops": len(path),
            "average_crowdedness": avg_crowdedness,
            "start_location": self.graph.get_location(start_id),
            "end_location": self.graph.get_location(end_id),
            "algorithm": "a_star",
            "mode": "low_crowd"
        }
