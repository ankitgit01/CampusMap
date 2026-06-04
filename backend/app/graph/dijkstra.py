"""
Dijkstra's algorithm for shortest path finding
"""
import heapq
from typing import Dict, List, Tuple, Optional
from app.graph.graph_builder import CampusGraph

class DijkstraRouter:
    """
    Implements Dijkstra's algorithm for finding shortest paths
    """
    
    def __init__(self, graph: CampusGraph):
        self.graph = graph
    
    def find_path(
        self,
        start_id: int,
        end_id: int,
        weight_key: str = "walking_time",
        avoid_blocked: bool = True,
        accessibility_required: bool = False
    ) -> Dict:
        """
        Find shortest path using Dijkstra's algorithm
        
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
        
        # Initialize distances and previous nodes
        distances = {node_id: float('inf') for node_id in self.graph.nodes}
        distances[start_id] = 0
        
        previous = {node_id: None for node_id in self.graph.nodes}
        visited = set()
        
        # Priority queue: (distance, node_id)
        pq = [(0, start_id)]
        edge_info = {}  # Track which edges we used
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            # Early termination if we reached the destination
            if current_node == end_id:
                break
            
            # Skip if this distance is greater than what we found
            if current_distance > distances[current_node]:
                continue
            
            # Check all neighbors
            for neighbor_id, edge_data in self.graph.get_neighbors(current_node):
                # Skip blocked routes
                if avoid_blocked and edge_data.get('is_blocked', False):
                    continue
                
                # Skip if accessibility required but route not accessible
                if accessibility_required and not edge_data.get('is_wheelchair_accessible', False):
                    continue
                
                # Calculate new distance
                weight = edge_data.get(weight_key, float('inf'))
                new_distance = current_distance + weight
                
                # Update if we found a shorter path
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_node
                    edge_info[neighbor_id] = edge_data
                    heapq.heappush(pq, (new_distance, neighbor_id))
        
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
            "algorithm": "dijkstra",
            "mode": "shortest_time" if weight_key == "walking_time" else "shortest_distance"
        }
    
    def find_accessible_path(
        self,
        start_id: int,
        end_id: int
    ) -> Dict:
        """
        Find most accessible path (avoiding stairs, steep slopes, etc.)
        """
        if not self.graph.is_valid_node(start_id) or not self.graph.is_valid_node(end_id):
            return {"error": "Invalid location"}
        
        # Initialize with inverse accessibility scores as weights
        distances = {node_id: float('inf') for node_id in self.graph.nodes}
        distances[start_id] = 0
        
        previous = {node_id: None for node_id in self.graph.nodes}
        visited = set()
        
        pq = [(0, start_id)]
        edge_info = {}
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            if current_node in visited:
                continue
            
            visited.add(current_node)
            
            if current_node == end_id:
                break
            
            if current_distance > distances[current_node]:
                continue
            
            for neighbor_id, edge_data in self.graph.get_neighbors(current_node):
                # Skip blocked routes
                if edge_data.get('is_blocked', False):
                    continue
                
                # Penalize stairs and slopes
                penalty = 0
                if edge_data.get('has_stairs', False):
                    penalty += 1000
                if edge_data.get('has_slope', False):
                    penalty += 500
                
                # Use inverse of accessibility score
                accessibility_cost = (1 - edge_data.get('accessibility_score', 0)) * 1000
                weight = accessibility_cost + penalty
                
                new_distance = current_distance + weight
                
                if new_distance < distances[neighbor_id]:
                    distances[neighbor_id] = new_distance
                    previous[neighbor_id] = current_node
                    edge_info[neighbor_id] = edge_data
                    heapq.heappush(pq, (new_distance, neighbor_id))
        
        # Reconstruct path
        path = []
        current = end_id
        
        if previous[current] is None and current != start_id:
            return {"error": "No accessible path found"}
        
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
            "algorithm": "dijkstra",
            "mode": "accessible"
        }
